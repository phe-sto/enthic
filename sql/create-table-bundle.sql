CREATE TABLE IF NOT EXISTS bundle
(
    siren INT PRIMARY KEY NOT NULL,
    declaration YEAR(4) NOT NULL,
    bundle CHAR(3) NOT NULL,
    amount INT NOT NULL
);