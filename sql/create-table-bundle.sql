CREATE TABLE IF NOT EXISTS bundle
(
    siren INT NOT NULL,
    declaration YEAR(4) NOT NULL,
    accountability TINYINT NOT NULL,
    bundle TINYINT NOT NULL,
    amount BIGINT NOT NULL
);