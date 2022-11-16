create table users
(
    id            bigint primary key generated always as identity,
    first_name    varchar(50)        not null,
    last_name     varchar(50)        not null,
    email         varchar(50)        not null unique,
    password      varchar(255)       not null,
    editor_status bool default false not null
);
create table universes
(
    id   serial primary key,
    name varchar(50) not null unique
);
create table products
(
    id       serial primary key,
    title    varchar(100) not null,
    category varchar(50)  not null,
    universe int          not null,
    cost     int          not null,
    img_url  varchar      not null,
    constraint fk_universe
        foreign key (universe)
            references universes (id)
            on delete set null
);
create table cart
(
    id         serial primary key,
    product_id int           not null,
    user_id    int           not null,
    count      int default 1 not null,
    constraint fk_product
        foreign key (product_id)
            references products (id)
            on delete cascade,
    constraint fk_user
        foreign key (user_id)
            references users (id)
            on delete cascade
);
create table wishlist
(
    id         serial primary key,
    product_id int        not null,
    user_id    int        not null,
    constraint fk_product
        foreign key (product_id)
            references products (id)
            on delete cascade,
    constraint fk_user
        foreign key (user_id)
            references users (id)
            on delete cascade
);

create table orders(
    id serial primary key,
    user_id int not null ,
    address varchar(50) not null,
    total_price int not null,
    constraint fk_user
        foreign key (user_id)
            references users (id)
            on delete cascade
);

