CREATE TABLE IF NOT EXISTS bundle
(
    siren CHAR(9) NOT NULL,
    declaration YEAR(4) NOT NULL,
    bundle CHAR(3) NOT NULL,
    amount BIGINT NOT NULL
);