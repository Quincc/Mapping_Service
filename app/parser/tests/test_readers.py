"""
Мини-тесты на функции parse_file().

✔ проверяем, что CSV, XLSX и JSON читаются
✖ unsupported формат бросает исключение
"""
import pandas as pd
import pytest
from pathlib import Path

from app.parser.exceptions import UnsupportedFormat
from app.parser.readers import parse_file


def _make_tmp(path: Path, df: pd.DataFrame):
    if path.suffix == ".csv":
        df.to_csv(path, index=False)
    elif path.suffix == ".xlsx":
        df.to_excel(path, index=False)
    else:
        df.to_json(path, orient="records", lines=True)


@pytest.mark.parametrize("ext", [".csv", ".xlsx", ".json"])
def test_supported(ext, tmp_path: Path):
    df_in = pd.DataFrame({"a": [1, 2]})
    file = tmp_path / f"sample{ext}"
    _make_tmp(file, df_in)

    df_out = parse_file(file)
    pd.testing.assert_frame_equal(df_in, df_out)


def test_unsupported(tmp_path: Path):
    file = tmp_path / "sample.txt"
    file.write_text("noop")
    with pytest.raises(UnsupportedFormat):
        parse_file(file)