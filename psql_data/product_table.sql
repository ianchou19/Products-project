CREATE TABLE product (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(50),
    stock          INTEGER,
    price          DECIMAL(18,2),
    description    VARCHAR(255),
    category       VARCHAR(50)
);
