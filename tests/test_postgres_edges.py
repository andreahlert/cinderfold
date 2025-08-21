from cinderfold.postgres import from_information_schema


def test_bare_list_accepted():
    payload = [
        {"name": "u", "columns": [{"name": "id", "type": "integer", "pk": True, "nullable": False}]}
    ]
    s = from_information_schema(payload)
    assert s.table("u").column("id").pk is True


def test_indexes_loaded():
    payload = {"tables": [
        {
            "name": "u",
            "columns": [{"name": "id", "type": "integer", "pk": True, "nullable": False}],
            "indexes": [{"name": "ix_u_id", "columns": ["id"], "unique": True}],
        }
    ]}
    s = from_information_schema(payload)
    assert s.table("u").indexes[0].unique is True


def test_foreign_keys_loaded_with_actions():
    payload = {"tables": [
        {
            "name": "u",
            "columns": [{"name": "id", "type": "integer", "pk": True, "nullable": False}],
        },
        {
            "name": "o",
            "columns": [
                {"name": "id", "type": "integer", "pk": True, "nullable": False},
                {"name": "uid", "type": "integer", "nullable": False},
            ],
            "foreign_keys": [{
                "name": "fk_o_u", "columns": ["uid"], "ref_table": "u", "ref_columns": ["id"],
                "on_delete": "cascade",
            }],
        }
    ]}
    s = from_information_schema(payload)
    fk = s.table("o").foreign_keys[0]
    assert fk.ref_table == "u" and fk.on_delete == "cascade"


def test_default_nullable_true_when_missing():
    payload = {"tables": [
        {"name": "u", "columns": [{"name": "id", "type": "integer", "pk": True}]}
    ]}
    s = from_information_schema(payload)
    assert s.table("u").column("id").nullable is True


def test_empty_payload():
    assert from_information_schema({"tables": []}).tables == ()
