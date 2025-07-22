from pathlib import Path

from cinderfold.parser import parse
from cinderfold.serial import from_dict, from_json, to_dict, to_json


FIX = Path(__file__).resolve().parent.parent / "fixtures"


def test_roundtrip_dict():
    s = parse((FIX / "blog_v2.dsl").read_text())
    again = from_dict(to_dict(s))
    assert again == s


def test_roundtrip_json():
    s = parse((FIX / "blog_v1.dsl").read_text())
    again = from_json(to_json(s))
    assert again == s


def test_minimal_payload():
    payload = {"tables": [
        {"name": "u", "columns": [{"name": "id", "type": "int", "pk": True, "not_null": True}]}
    ]}
    s = from_dict(payload)
    assert s.table("u").columns[0].pk is True
    assert s.table("u").columns[0].nullable is False


def test_default_actions_dropped_from_output():
    s = parse("table o { id: int pk not_null; uid: int not_null; "
              "fk fk_o_u (uid) -> u (id); }")
    d = to_dict(s)
    fk = d["tables"][0]["foreign_keys"][0]
    assert "on_delete" not in fk and "on_update" not in fk
