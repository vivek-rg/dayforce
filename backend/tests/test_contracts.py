import pytest
from app.shared import contracts

from scripts.export_contracts import example, generate


def test_generated_contract_files_are_current():
    for path, expected in generate().items():
        assert path.read_text(encoding="utf-8") == expected, str(path)


def test_every_shared_model_has_a_valid_documented_example():
    import json

    generated = generate()
    document = json.loads(
        next(value for path, value in generated.items() if path.suffix == ".json")
    )
    checked = 0
    for name, schema in document["components"]["schemas"].items():
        model = getattr(contracts, name, None)
        if isinstance(model, type) and issubclass(model, contracts.Contract):
            model.model_validate(example(schema, document))
            checked += 1
    assert checked >= 30


@pytest.mark.parametrize("path", ["/api/health", "/api/bootstrap", "/api/hires", "/api/sessions"])
def test_expected_handoff_paths_exist(path):
    from app.main import app

    assert path in app.openapi()["paths"]
