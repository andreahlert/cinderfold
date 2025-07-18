table users {
    id: int pk not_null;
    email: text not_null unique;
    display_name: text;
    created_at: timestamp not_null default = now();
}

table posts {
    id: int pk not_null;
    user_id: int not_null;
    title: text not_null;
    body: text not_null;
    published_at: timestamp;
    slug: text not_null unique;
    index ix_posts_user (user_id);
    index ix_posts_slug (slug) unique;
    fk fk_posts_user (user_id) -> users (id) on_delete = cascade;
}

table comments {
    id: int pk not_null;
    post_id: int not_null;
    author_id: int not_null;
    body: text not_null;
    index ix_comments_post (post_id);
    fk fk_comments_post (post_id) -> posts (id) on_delete = cascade;
    fk fk_comments_author (author_id) -> users (id) on_delete = set_null;
}

table tags {
    id: int pk not_null;
    name: text not_null unique;
}

table post_tags {
    post_id: int not_null;
    tag_id: int not_null;
    fk fk_pt_post (post_id) -> posts (id) on_delete = cascade;
    fk fk_pt_tag (tag_id) -> tags (id) on_delete = cascade;
    index ix_pt_post_tag (post_id, tag_id) unique;
}
