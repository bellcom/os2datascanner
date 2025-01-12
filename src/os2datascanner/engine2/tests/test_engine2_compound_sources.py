import os.path
import unittest

from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.conversions import convert


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data")


def try_apply(sm, source, rule):
    for handle in source.handles(sm):
        derived = Source.from_handle(handle, sm)
        if derived:
            yield from try_apply(sm, derived, rule)
        else:
            resource = handle.follow(sm)
            representation = convert(resource, rule.operates_on)
            if representation:
                yield from rule.match(representation.value)


class Engine2CompoundSourceTest(unittest.TestCase):
    def setUp(self):
        self.rule = CPRRule(modulus_11=False, ignore_irrelevant=False)

    def run_rule(self, source, sm, offset=0):
        """spredsheets are converted to html, which is then converted to text. The html
        conversion preserves newlines and tabs, inserted between cells. This results
        in @offset != 0

        """
        results = list(try_apply(sm, source, self.rule))
        self.assertEqual(
                results,
                [
                    {
                        "offset": offset,
                        "match": "1310XXXXXX",
                        "context": "XXXXXX-XXXX",
                        "context_offset": 0,
                        "sensitivity": None,
                        "probability": 1.0
                    }
                ])

    def run_rule_on_handle(self, handle, offset=0):
        with SourceManager() as sm:
            source = Source.from_handle(handle, sm)
            self.assertIsNotNone(
                    source,
                    "{0} couldn't be made into a Source".format(handle))
            self.run_rule(source, sm, offset)

    def test_odt(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "libreoffice/embedded-cpr.odt")))

    def test_pdf(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "pdf/embedded-cpr.pdf")))

    def test_doc(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "msoffice/embedded-cpr.doc")))

    def test_docx(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "msoffice/embedded-cpr.docx")))

    def test_ods(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "libreoffice/test.ods")),
                offset=8)

    def test_xls(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "msoffice/test.xls")),
                offset=8)

    def test_xlsx(self):
        self.run_rule_on_handle(
                FilesystemHandle.make_handle(
                        os.path.join(
                                test_data_path,
                                "msoffice/test.xlsx")),
                offset=8)

    def test_corrupted_doc(self):
        corrupted_doc_handle = FilesystemHandle.make_handle(
                os.path.join(
                        test_data_path, "msoffice/corrupted/test.trunc.doc"))
        corrupted_doc = Source.from_handle(corrupted_doc_handle)
        with SourceManager() as sm:
            self.assertEqual(
                    list(corrupted_doc.handles(sm)),
                    [],
                    "unrecognised CDFV2 document should be empty and wasn't")

    def test_libreoffice_size(self):
        large_doc_handle = FilesystemHandle.make_handle(
                os.path.join(
                        test_data_path, "libreoffice/html-explosion.ods"))
        large_doc = Source.from_handle(large_doc_handle)
        with SourceManager() as sm:
            for h in large_doc.handles(sm):
                if h.name.endswith(".html"):
                    r = h.follow(sm)
                    self.assertLess(
                            r.get_size().value,
                            1048576,
                            "LibreOffice HTML output was too big")
