"""A representative starting schema for the experiment."""

from cinderfold.parser import parse


SEED_TEXT = """
table users {
    id: int pk not_null;
    email: text not_null unique;
    name: text;
    created_at: timestamp not_null default = now();
    updated_at: timestamp;
    is_active: boolean default = true;
}

table orders {
    id: int pk not_null;
    user_id: int not_null;
    total: decimal not_null;
    status: text not_null default = "pending";
    placed_at: timestamp not_null;
    shipped_at: timestamp;
}

table order_items {
    id: int pk not_null;
    order_id: int not_null;
    sku: text not_null;
    qty: int not_null default = 1;
    unit_price: decimal not_null;
}

table products {
    sku: text pk not_null;
    name: text not_null;
    price: decimal not_null;
    inventory: int not_null default = 0;
    discontinued: boolean default = false;
}

table audit_events {
    id: int pk not_null;
    actor: text not_null;
    action: text not_null;
    at: timestamp not_null default = now();
    payload: text;
}
"""


def seed():
    return parse(SEED_TEXT)
