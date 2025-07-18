table users {
    id: int pk not_null;
    email: text not_null unique;
    created_at: timestamp not_null default = now();
}

table posts {
    id: int pk not_null;
    user_id: int not_null;
    title: text not_null;
    body: text;
    published_at: timestamp;
    index ix_posts_user (user_id);
    fk fk_posts_user (user_id) -> users (id) on_delete = cascade;
}

table comments {
    id: int pk not_null;
    post_id: int not_null;
    author: text not_null;
    body: text not_null;
    index ix_comments_post (post_id);
    fk fk_comments_post (post_id) -> posts (id) on_delete = cascade;
}
