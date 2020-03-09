CREATE TABLE IF NOT EXISTS bundle
(
    siren INT NOT NULL,
    declaration YEAR(4) NOT NULL,
    bundle CHAR(3) NOT NULL,
    amount FLOAT NOT NULL
);