CREATE TABLE IF NOT EXISTS identity
(
    siren INT PRIMARY KEY NOT NULL,
    denomination VARCHAR(100) NOT NULL,
    ape CHAR(5) NOT NULL,
    postal_code CHAR(5) NOT NULL,
    town VARCHAR(25) NOT NULL,
    accountability CHAR(1) NOT NULL,
    devise CHAR(3) NOT NULL,
    FULLTEXT(denomination)
) ENGINE=InnoDB;