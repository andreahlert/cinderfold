from cinderfold.postgres import from_information_schema


def test_from_dict_payload():
    payload = {"tables": [
        {"name": "users",
         "columns": [
             {"name": "id", "type": "integer", "pk": True, "nullable": False},
             {"name": "email", "type": "text", "nullable": False, "unique": True},
         ]},
        {"name": "orders",
         "columns": [
             {"name": "id", "type": "integer", "pk": True, "nullable": False},
             {"name": "user_id", "type": "integer", "nullable": False},
         ],
         "foreign_keys": [
             {"name": "fk_orders_user", "columns": ["user_id"],
              "ref_table": "users", "ref_columns": ["id"],
              "on_delete": "cascade"},
         ]},
    ]}
    s = from_information_schema(payload)
    assert {t.name for t in s.tables} == {"users", "orders"}
    assert s.table("orders").foreign_keys[0].on_delete == "cascade"


def test_from_list_payload_also_accepted():
    payload = [
        {"name": "u",
         "columns": [{"name": "id", "type": "int", "pk": True, "nullable": False}]}
    ]
    s = from_information_schema(payload)
    assert s.table("u") is not None


def test_indexes_and_unique_round_trip():
    payload = {"tables": [
        {"name": "t",
         "columns": [{"name": "x", "type": "int"}],
         "indexes": [{"name": "ix_t_x", "columns": ["x"], "unique": True}]}
    ]}
    s = from_information_schema(payload)
    assert s.table("t").indexes[0].unique is True
