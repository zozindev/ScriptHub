import json
import os
import subprocess
import sys
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from PIL import Image

from core.ffmpeg_utils import (
    build_ffmpeg_cmd,
    recommended_transcode_workers,
    run_cmd,
    transcode_video,
)
from modules.excel_updater import (
    build_excel_update_download,
    dataframe_to_excel_values,
    filter_deleted_respondents,
    load_excel_update_data,
)
from modules.file_utils import build_zip_bytes, deduplicate_filenames
from modules.html_validator import is_html_error
from modules.image_bg_remover import (
    build_preview_bytes,
    recommended_image_workers,
    remove_near_white_background,
)
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


class FileAndMediaRegressionTests(unittest.TestCase):
    def test_near_white_background_conversion_matches_existing_threshold_rules(self):
        image = Image.new("RGBA", (4, 1))
        image.putdata(
            [
                (255, 255, 255, 255),
                (241, 242, 243, 128),
                (240, 255, 255, 200),
                (10, 20, 30, 40),
            ]
        )

        result = list(remove_near_white_background(image).getdata())

        self.assertEqual(
            result,
            [
                (255, 255, 255, 0),
                (255, 255, 255, 0),
                (240, 255, 255, 200),
                (10, 20, 30, 40),
            ],
        )

    def test_shared_file_helpers_preserve_order_and_duplicate_naming(self):
        named_data = [("result.png", b"one"), ("result.png", b"two")]
        deduplicated = deduplicate_filenames(named_data)

        self.assertEqual(
            deduplicated,
            [("result.png", b"one"), ("result (1).png", b"two")],
        )

        with zipfile.ZipFile(BytesIO(build_zip_bytes(deduplicated))) as archive:
            self.assertEqual(archive.namelist(), ["result.png", "result (1).png"])
            self.assertEqual(archive.read("result.png"), b"one")
            self.assertEqual(archive.getinfo("result.png").compress_type, zipfile.ZIP_STORED)

        mixed_archive = build_zip_bytes([("image.PNG", b"image"), ("notes.txt", b"text" * 100)])
        with zipfile.ZipFile(BytesIO(mixed_archive)) as archive:
            self.assertEqual(archive.getinfo("image.PNG").compress_type, zipfile.ZIP_STORED)
            self.assertEqual(archive.getinfo("notes.txt").compress_type, zipfile.ZIP_DEFLATED)

    def test_background_preview_and_worker_limits_bound_memory_usage(self):
        image = Image.new("RGBA", (1200, 800), "white")
        preview_data = build_preview_bytes(image)

        with Image.open(BytesIO(preview_data)) as preview:
            self.assertLessEqual(preview.width, 320)
            self.assertLessEqual(preview.height, 320)

        self.assertEqual(recommended_image_workers(0, cpu_count=16), 0)
        self.assertEqual(recommended_image_workers(2, cpu_count=16), 2)
        self.assertEqual(recommended_image_workers(20, cpu_count=16), 4)
        self.assertEqual(recommended_image_workers(20, cpu_count=2), 2)
        with patch("modules.image_bg_remover.os.cpu_count", return_value=8):
            self.assertEqual(recommended_image_workers(20), 4)

    def test_html_validation_keeps_existing_stack_rules(self):
        self.assertFalse(is_html_error("일반 텍스트"))
        self.assertFalse(is_html_error("<b>정상</b><br>"))
        self.assertTrue(is_html_error("<b><u>오류</b></u>"))
        self.assertTrue(is_html_error("<b>닫히지 않음"))


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

    def test_dataframe_conversion_builds_one_com_ready_matrix(self):
        dataframe = pd.DataFrame({"A": [1, None], "B": ["x", "y"]})

        values = dataframe_to_excel_values(dataframe)

        self.assertEqual(values[0], ["A", "B"])
        self.assertEqual(values[1], [1.0, "x"])
        self.assertEqual(values[2], [None, "y"])

    def test_excel_loader_reuses_open_workbooks_for_sheet_parsing(self):
        new_file = BytesIO()
        with pd.ExcelWriter(new_file, engine="openpyxl") as writer:
            pd.DataFrame(
                {"Respondent.Serial": ["1", "2"], "Value": [10, 20]}
            ).to_excel(writer, sheet_name="Data", index=False)
        new_file.seek(0)

        old_file = BytesIO()
        with pd.ExcelWriter(old_file, engine="openpyxl") as writer:
            pd.DataFrame({"Respondent.Serial": ["2"]}).to_excel(
                writer,
                sheet_name="del",
                index=False,
            )
            pd.DataFrame({"Status": []}).to_excel(writer, sheet_name="Status", index=False)
        old_file.seek(0)

        updated, has_del, has_status = load_excel_update_data(new_file, old_file)

        self.assertEqual(updated["Respondent.Serial"].astype(str).tolist(), ["1"])
        self.assertTrue(has_del)
        self.assertTrue(has_status)


class FfmpegOptimizationTests(unittest.TestCase):
    def test_worker_count_avoids_software_encoder_oversubscription(self):
        self.assertEqual(recommended_transcode_workers(0, use_qsv=False), 0)
        self.assertEqual(recommended_transcode_workers(5, use_qsv=False), 1)
        self.assertEqual(recommended_transcode_workers(5, use_qsv=True), 2)

    def test_ffmpeg_command_suppresses_progress_output(self):
        command = build_ffmpeg_cmd(
            Path("input.mp4"),
            Path("output.mp4"),
            568,
            320,
            30,
            use_qsv=False,
        )

        self.assertIn("-loglevel", command)
        self.assertIn("error", command)
        self.assertIn("-nostats", command)
        self.assertIn("-nostdin", command)

    def test_run_cmd_discards_unused_stdout_and_sets_timeout(self):
        completed = subprocess.CompletedProcess([], 0, stdout=None, stderr="")
        with patch("core.ffmpeg_utils.subprocess.run", return_value=completed) as mocked_run:
            result = run_cmd(["ffmpeg"], timeout=7, capture_stdout=False)

        self.assertIs(result, completed)
        kwargs = mocked_run.call_args.kwargs
        self.assertIs(kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(kwargs["timeout"], 7)

    def test_qsv_failure_falls_back_to_x264(self):
        qsv_failure = subprocess.CompletedProcess([], 1, stdout=None, stderr="qsv unavailable")
        x264_success = subprocess.CompletedProcess([], 0, stdout=None, stderr="")

        with patch(
            "core.ffmpeg_utils.run_cmd",
            side_effect=[qsv_failure, x264_success],
        ) as mocked_run:
            result, encoder, qsv_error = transcode_video(
                Path("input.mp4"),
                Path("output.mp4"),
                568,
                320,
                32,
                30,
                use_qsv=True,
            )

        self.assertIs(result, x264_success)
        self.assertEqual(encoder, "x264")
        self.assertEqual(qsv_error, "qsv unavailable")
        self.assertIn("h264_qsv", mocked_run.call_args_list[0].args[0])
        self.assertIn("libx264", mocked_run.call_args_list[1].args[0])


class StartupOptimizationTests(unittest.TestCase):
    def test_app_import_does_not_eagerly_import_feature_modules(self):
        project_root = Path(__file__).resolve().parents[1]
        code = (
            "import sys; import app; "
            "feature_modules = [name for name in sys.modules if name.startswith('modules.')]; "
            "print('\\n'.join(feature_modules))"
        )
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(completed.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
