import json
import os
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from modules.excel_updater import build_excel_update_download, filter_deleted_respondents
from modules.mdd_generator import generate_mdd_script
from modules.output_utils import javascript_string_literal
from modules.qlib_to_mdd import process_script_content
from modules.script_converter import convert_script_lines


class UploadedFileStub:
    def __init__(self, name, value):
        self.name = name
        self._value = value

    def getvalue(self):
        return self._value


class OutputSafetyTests(unittest.TestCase):
    def test_javascript_literal_does_not_allow_script_tag_breakout(self):
        payload = '한글\u2028ok</script><script>alert("x")</script>'
        literal = javascript_string_literal(payload)

        self.assertNotIn("</script>", literal.lower())
        self.assertNotIn("\u2028", literal)
        self.assertEqual(json.loads(literal), payload)

    def test_script_converter_keeps_normal_output_and_escapes_quotes(self):
        dim_normal, nf_normal = convert_script_lines(["Nexen", "기타(other)", "없음(exe)"])
        self.assertEqual(
            dim_normal,
            '{\n    _1 "Nexen",\n    _98 "기타" fix other,\n    _99@ "없음" fix exclusive\n};',
        )
        self.assertEqual(
            nf_normal,
            '1:Nexen*PROPERTIES "DIMELE=_1"\n'
            '98:기타*OPEN *NOCON *PROPERTIES "DIMELE=_98"\n'
            '99:없음*PROPERTIES "DIMELE=_99@"*NMUL *NOCON',
        )

        dim_quoted, _ = convert_script_lines(['브랜드 "A"'])
        self.assertIn(r'브랜드 \"A\"', dim_quoted)

    def test_mdd_script_escapes_question_and_attribute_quotes(self):
        df = pd.DataFrame(
            [
                {
                    "Question Number": "Q1",
                    "Type": "single",
                    "Question Text": '질문 "A"',
                    "Attribute Number": 1,
                    "Attribute Text": '보기 "B"',
                    "Attribute exe": "",
                }
            ]
        )
        generated = generate_mdd_script(df, {"single": ""})

        self.assertIn(r'Q1 "질문 \"A\""', generated)
        self.assertIn(r'_1 "보기 \"B\""', generated)


class QlibRegressionTests(unittest.TestCase):
    def test_plain_short_content_is_returned_without_index_error(self):
        self.assertEqual(process_script_content("plain"), "plain")
        self.assertEqual(process_script_content(""), "")


class ExcelUpdaterRegressionTests(unittest.TestCase):
    def test_deletion_filter_excludes_serials_and_ignores_blank_deletions(self):
        source = pd.DataFrame({"Respondent.Serial": ["1", "2", None], "Value": [10, 20, 30]})
        deleted = pd.DataFrame({"Respondent.Serial": ["2", None, ""]})
        with patch("modules.excel_updater.pd.read_excel", return_value=deleted):
            result = filter_deleted_respondents(source, "old.xlsx")

        self.assertEqual(result["Respondent.Serial"].tolist(), ["1", None])

    def test_deletion_filter_fails_when_required_column_is_missing(self):
        source = pd.DataFrame({"Different.Serial": ["1"]})
        with self.assertRaisesRegex(ValueError, "Respondent.Serial"):
            filter_deleted_respondents(source, "not-used.xlsx")

    def test_deletion_filter_fails_when_delete_sheet_cannot_be_read(self):
        source = pd.DataFrame({"Respondent.Serial": ["1"]})
        with patch("modules.excel_updater.pd.read_excel", side_effect=ValueError("missing column")):
            with self.assertRaisesRegex(ValueError, "del"):
                filter_deleted_respondents(source, "old.xlsx")

    def test_uploaded_excel_processing_uses_isolated_temporary_directories(self):
        old_file = UploadedFileStub("old.xlsx", b"old")
        new_file = UploadedFileStub("new.xlsx", b"new")
        used_directories = []

        def fake_update(old_path, new_path, output_path):
            used_directories.append(os.path.dirname(old_path))
            self.assertEqual(os.path.dirname(old_path), os.path.dirname(new_path))
            self.assertEqual(os.path.dirname(old_path), os.path.dirname(output_path))
            with open(output_path, "wb") as output:
                output.write(b"result")
            return []

        with patch("modules.excel_updater.update_excel_data_with_pywin32", side_effect=fake_update):
            first = build_excel_update_download(old_file, new_file)
            second = build_excel_update_download(old_file, new_file)

        self.assertEqual(first[0], b"result")
        self.assertEqual(first[1], "new_updated.xlsx")
        self.assertEqual(second[0], b"result")
        self.assertEqual(len(set(used_directories)), 2)
        self.assertTrue(all(not os.path.exists(path) for path in used_directories))


if __name__ == "__main__":
    unittest.main()
