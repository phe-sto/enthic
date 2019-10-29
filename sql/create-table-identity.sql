CREATE TABLE IF NOT EXISTS identity
(
    siren INT PRIMARY KEY NOT NULL,
    denomination VARCHAR(100) NOT NULL,
    accountability CHAR(1) NOT NULL,
    devise CHAR(3) NOT NULL
);