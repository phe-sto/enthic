CREATE TABLE IF NOT EXISTS identity
(
    siren INT PRIMARY KEY NOT NULL,
    denomination VARCHAR(100) NOT NULL,
    ape SMALLINT NOT NULL,
    postal_code CHAR(5) NOT NULL,
    town VARCHAR(60) NOT NULL,
    FULLTEXT(denomination)
) ENGINE=InnoDB;
