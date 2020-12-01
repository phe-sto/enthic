CREATE TABLE IF NOT EXISTS annual_statistics
(
    siren INT NOT NULL,
    declaration YEAR(4) NOT NULL,
    stats_type TINYINT,
    value FLOAT,
    UNIQUE( `siren`, `declaration`)
);
