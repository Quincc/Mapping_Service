"""
Тестируем apply_mapping поверх `MappingConfig`.
"""
import pandas as pd
from app.mapping.engine import apply_mapping
from app.mapping.schemas import MappingConfig, MappingRule

def test_apply_mapping():
    src = pd.DataFrame({"customer_name": [" ivan ivanov "]})
    cfg = MappingConfig(
        project_id="demo",
        rules=[
            MappingRule(source="customer_name", target="name", transform="trim", type="string")
        ],
    )
    out = apply_mapping(src, cfg)
    assert out.iloc[0]["name"] == "ivan ivanov"
