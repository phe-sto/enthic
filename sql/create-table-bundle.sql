CREATE TABLE IF NOT EXISTS bundle
(
    siren CHAR(9) PRIMARY KEY NOT NULL,
    declaration YEAR(4) NOT NULL,
    bundle CHAR(3) NOT NULL,
    amount INT NOT NULL
);