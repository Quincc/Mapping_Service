"""Юнит‑тесты движка проверки."""

import pandas as pd
from app.quality.checker import check_dataframe

def test_missing_required():
    df = pd.DataFrame({"email": ["a@x"], "name": ["A"]})
    qc = check_dataframe(df)
    assert any(i.type == "missing_field" and i.column == "birthdate"
               for i in qc.issues)
