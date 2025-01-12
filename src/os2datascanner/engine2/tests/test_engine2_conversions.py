import os.path
import unittest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.conversions.registry import convert


here_path = os.path.dirname(__file__)
image_handle = FilesystemHandle.make_handle(
    os.path.join(here_path, "data/ocr/good/cpr.png")
)
html_handle = FilesystemHandle.make_handle(
    os.path.join(here_path, "data/html/simple.html")
)
empty_handle = FilesystemHandle.make_handle(
    os.path.join(here_path, "data/empty_file")
)


class Engine2ConversionTest(unittest.TestCase):
    def setUp(self):
        self._sm = SourceManager()

        self._ir = image_handle.follow(self._sm)
        self._hr = html_handle.follow(self._sm)
        self._er = empty_handle.follow(self._sm)

    def tearDown(self):
        self._sm.clear()

    def test_last_modified(self):
        self.assertIsNotNone(
            convert(self._ir, OutputType.LastModified).value)

    def test_image_dimensions(self):
        self.assertEqual(
            convert(self._ir, OutputType.ImageDimensions).value,
            (896, 896)
        )

    def test_fallback(self):
        self.assertEqual(
            convert(self._ir, OutputType.AlwaysTrue).value,
            True)

    def test_dummy(self):
        with self.assertRaises(KeyError):
            convert(self._ir, OutputType.NoConversions)

    def test_html(self):
        self.assertEqual(
            # f"{'':8}" insert 8 ' '(spaces)
            f"\n{'':8}\n{'':12}"
            "This is only a test."
            f"\n{'':8}\n{'':12}\n{'':16}"
            "There's one paragraph,"
            f"\n{'':16}"
            "and then there's the other"
            f"\n{'':16}"
            "paragraph."
            f"\n{'':8}\n{'':4}",
            convert(self._hr, OutputType.Text).value,
            "converted HTML do not match the expected result",
        )

    def test_empty_html(self):
        self.assertEqual(
            convert(self._er, OutputType.Text, mime_override="text/html"),
            None,
            "empty HTML document did not produce empty conversion",
        )
