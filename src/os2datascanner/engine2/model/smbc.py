import io
from os import stat_result, O_RDONLY
import enum
import logging
import smbc
from typing import Optional
from urllib.parse import quote, unquote, urlsplit
from datetime import datetime
from contextlib import contextmanager

from ..utilities.backoff import run_with_backoff
from ..conversions.types import OutputType
from ..conversions.utilities.results import MultipleResults
from .smb import SMBSource, make_smb_url, compute_domain
from .core import Source, Handle, FileResource
from .file import stat_attributes
from .utilities import NamedTemporaryResource


logger = logging.getLogger(__name__)

XATTR_DOS_ATTRIBUTES = "system.dos_attr.mode"
"""The attribute name for a file's mode flags. (This is not documented in
pysmbc, but it is in the underlying libsmbclient library.)"""


IGNORABLE_SMBC_EXCEPTIONS = (
        smbc.NoEntryError, smbc.NotDirectoryError, smbc.PermissionError)
"""The exceptions to ignore during SMBC exploration. Note that this does not
exclude write errors or connection errors."""


class Mode(enum.IntFlag):
    """A convenience enumeration for manipulating SMB file mode flags."""
    # description of flags mapping
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb/65e0c225-5925-44b0-8104-6b91339c709f
    # https://github.com/samba-team/samba/blob/master/source3/include/libsmbclient.h#L200
    READ_ONLY = 0x01
    HIDDEN = 0x02
    SYSTEM = 0x04
    VOLUME_ID = 0x08
    DIRECTORY = 0x10
    ARCHIVE = 0x20

    @staticmethod
    def for_url(context: smbc.Context, url: str) -> Optional['Mode']:
        """Attempts to convert the mode flags retrieved from the given smb://
        URL to a Mode."""
        try:
            mode_ = context.getxattr(url, XATTR_DOS_ATTRIBUTES)
            return Mode(int(mode_, 16))
        except (ValueError, *IGNORABLE_SMBC_EXCEPTIONS):
            return None


class SMBCSource(Source):
    type_label = "smbc"
    eq_properties = (
            "_unc", "_user", "_password", "_domain", "_skip_super_hidden")

    def __init__(self, unc, user=None, password=None, domain=None,
            driveletter=None, *, skip_super_hidden: bool = False):
        self._unc = unc
        self._user = user
        self._password = password
        self._domain = domain if domain is not None else compute_domain(unc)
        self._driveletter = driveletter
        self._skip_super_hidden = skip_super_hidden

    @property
    def unc(self):
        return self._unc

    @property
    def driveletter(self):
        return self._driveletter

    def __auth_handler(self, server, share, workgroup, username, password):
        """Returns the (workgroup, username, password) tuple expected of
        pysmbc authentication functions."""
        return (self._domain or "WORKGROUP",
                self._user or "GUEST", self._password or "")

    def _generate_state(self, sm):
        c = smbc.Context(auth_fn=self.__auth_handler)
        # Session cleanup for pysmbc is handled by the Python garbage
        # collector (groan...), so it's *critical* that no objects have a live
        # reference to this smbc.Context when this function completes
        yield (self._to_url(), c)

    def censor(self):
        return SMBCSource(self.unc, None, None, None, self.driveletter)

    def handles(self, sm):
        url, context = sm.open(self)
        def handle_dirent(parents, entity):
            name = entity.name

            here = parents + [entity]
            path = '/'.join([h.name for h in here])
            url_here = url + "/" + path

            if self._skip_super_hidden:
                mode = Mode.for_url(context, url_here)

                # If this object is super-hidden -- that is, if it has the
                # hidden bit set plus either the system bit or the "~"
                # character at the start of its name -- then ignore it
                if (mode is not None
                        and mode & Mode.HIDDEN
                        and (mode & Mode.SYSTEM
                                or name.startswith("~"))):
                    logger.info(f"skipping super-hidden object {path}")
                    return

            if entity.smbc_type == smbc.DIR and name not in (".", ".."):
                try:
                    obj = context.opendir(url_here)
                    for dent in obj.getdents():
                        yield from handle_dirent(here, dent)
                except (ValueError, *IGNORABLE_SMBC_EXCEPTIONS):
                    pass
            elif entity.smbc_type == smbc.FILE:
                yield SMBCHandle(self, path)

        obj = context.opendir(url)
        for dent in obj.getdents():
            yield from handle_dirent([], dent)

    def to_url(self):
        return make_smb_url(
                "smbc", self._unc, self._user, self._domain, self._password)

    # For our own purposes, we need to be able to make a "smb://" URL to give
    # to pysmbc. That URL doesn't need to contain authentication details,
    # though, as our __auth_handler function takes care of that
    def _to_url(self):
        return make_smb_url("smb", self._unc, None, None, None)

    @staticmethod
    @Source.url_handler("smbc")
    def from_url(url):
        scheme, netloc, path, _, _ = urlsplit(url)
        match = SMBSource.netloc_regex.match(netloc)
        if match:
            return SMBCSource("//" + match.group("unc") + unquote(path),
                match.group("username"), match.group("password"),
                match.group("domain"))
        else:
            return None

    def to_json_object(self):
        return dict(**super().to_json_object(), **{
            "unc": self._unc,
            "user": self._user,
            "password": self._password,
            "domain": self._domain,
            "driveletter": self._driveletter,

            "skip_super_hidden": self._skip_super_hidden
        })

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return SMBCSource(
                obj["unc"], obj["user"], obj["password"], obj["domain"],
                obj["driveletter"],
                skip_super_hidden=obj.get("skip_super_hidden", False))


class _SMBCFile(io.RawIOBase):
    def __init__(self, obj):
        self._file = obj

    def readinto(self, b):
        data = self._file.read(len(b))
        count = len(data)
        b[0:count] = data
        return count

    def write(self, bytes):
        raise TypeError("_SMBCFile is read-only")

    def seek(self, pos, whence=0):
        r = self._file.lseek(pos, whence)
        if r != -1:
            return r
        else:
            raise IOError("lseek failed")

    def tell(self):
        r = self._file.lseek(0, io.SEEK_CUR)
        if r != -1:
            return r
        else:
            raise IOError("lseek failed")

    def truncate(self, n=None):
        raise TypeError("_SMBCFile is read-only")

    def close(self):
        if self._file:
            try:
                # XXX: for now, we can't propagate this error back up, because
                # we *need* this reference to be removed in all circumstances.
                # See SMBCSource._generate_state for the gruesome details

                # r = self._file.close()
                # if r and r < 0:
                #     raise IOError("Failed to close {0}".format(self), r)

                self._file.close()
            finally:
                self._file = None

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return True


class SMBCResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._mr = None

    def _generate_metadata(self):
        yield from super()._generate_metadata()
        yield "filesystem-owner-sid", self.get_owner_sid()

    def check(self) -> bool:
        try:
            _, context = self._get_cookie()
            context.stat(self._make_url())
            return True
        except smbc.NoEntryError:
            return False

    def _make_url(self):
        url, _ = self._get_cookie()
        return url + "/" + quote(self.handle.relative_path)

    def open_file(self):
        def _open_file():
            _, context = self._get_cookie()
            return context.open(self._make_url(), O_RDONLY)
        return run_with_backoff(_open_file, smbc.TimedOutError)[0]

    def get_xattr(self, attr):
        """Retrieves a SMB extended attribute for this file. (See the
        documentation for smbc.Context.getxattr for *most* of the supported
        attribute names.)"""
        def _get_xattr():
            _, context = self._get_cookie()
            # Don't attempt to catch the ValueError if attr isn't valid
            return context.getxattr(self._make_url(), attr)
        return run_with_backoff(_get_xattr, smbc.TimedOutError)[0]

    def unpack_stat(self):
        if not self._mr:
            f = self.open_file()
            try:
                self._mr = MultipleResults.make_from_attrs(
                        stat_result(f.fstat()), *stat_attributes)
                self._mr[OutputType.LastModified] = datetime.fromtimestamp(
                        self._mr["st_mtime"].value)
            finally:
                f.close()
        return self._mr

    def get_size(self):
        return self.unpack_stat()["st_size"]

    def get_last_modified(self):
        return self.unpack_stat().setdefault(OutputType.LastModified,
                super().get_last_modified())

    def get_owner_sid(self):
        """Returns the Windows security identifier of the owner of this file,
        which libsmbclient exposes as an extended attribute."""
        return self.get_xattr(smbc.XATTR_OWNER)

    @contextmanager
    def make_path(self):
        with NamedTemporaryResource(self.handle.name) as ntr:
            with ntr.open("wb") as f:
                with self.make_stream() as rf:
                    buf = rf.read(self.DOWNLOAD_CHUNK_SIZE)
                    while buf:
                        f.write(buf)
                        buf = rf.read(self.DOWNLOAD_CHUNK_SIZE)
            yield ntr.get_path()

    @contextmanager
    def make_stream(self):
        with _SMBCFile(self.open_file()) as fp:
            yield fp

    DOWNLOAD_CHUNK_SIZE = 1024 * 512


@Handle.stock_json_handler("smbc")
class SMBCHandle(Handle):
    type_label = "smbc"
    resource_type = SMBCResource

    @property
    def presentation(self):
        p = self.source.driveletter
        if p:
            p += ":"
        else:
            p = self.source.unc
        if p[-1] != "/":
            p += "/"
        return (p + self.relative_path).replace("/", "\\")

    @property
    def presentation_url(self):
        # Note that this implementation returns a Windows-friendly URL to the
        # underlying file -- i.e., one that uses the file: scheme and not smb:
        url = "file:"
        # XXX: our testing seems to indicate that drive letter URLs don't work
        # properly; we'll leave the disabled logic here for now...
        if False and self.source.driveletter:
            # Wikipedia indicates that local filesystem paths are represented
            # with an empty hostname followed by an absolute path...
            url += "///{0}:".format(self.source.driveletter)
        else:
            # ... and that remote ones are indicated with a hostname in the
            # usual place. Luckily the UNC already starts with two forward
            # slashes, so we can just paste it in here
            url += self.source.unc
        if url[-1] != "/":
            url += "/"
        return url + self.relative_path

    def censor(self):
        return SMBCHandle(self.source.censor(), self.relative_path)
