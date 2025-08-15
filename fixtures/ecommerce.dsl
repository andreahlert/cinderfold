table customers {
    id: int pk not_null;
    email: text not_null unique;
    full_name: text not_null;
    created_at: timestamp not_null default = now();
}

table products {
    id: int pk not_null;
    sku: text not_null unique;
    name: text not_null;
    price_cents: int not_null;
    active: bool not_null default = true;
}

table orders {
    id: int pk not_null;
    customer_id: int not_null;
    status: text not_null default = "pending";
    total_cents: int not_null;
    placed_at: timestamp not_null default = now();
    index ix_orders_customer (customer_id);
    fk fk_orders_customer (customer_id) -> customers (id) on_delete = restrict;
}

table order_items {
    id: int pk not_null;
    order_id: int not_null;
    product_id: int not_null;
    quantity: int not_null;
    unit_price_cents: int not_null;
    index ix_oi_order (order_id);
    index ix_oi_product (product_id);
    fk fk_oi_order (order_id) -> orders (id) on_delete = cascade;
    fk fk_oi_product (product_id) -> products (id) on_delete = restrict;
}

table inventory {
    product_id: int pk not_null;
    on_hand: int not_null default = 0;
    reserved: int not_null default = 0;
    fk fk_inv_product (product_id) -> products (id) on_delete = cascade;
}
