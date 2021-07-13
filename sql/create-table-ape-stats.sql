CREATE TABLE IF NOT EXISTS annual_ape_statistics
(
    ape SMALLINT NOT NULL,
    declaration YEAR(4) NOT NULL,
    stats_type TINYINT,
    percentile TINYINT,
    value FLOAT,
    count INT,
    UNIQUE( `ape`, `declaration`, `stats_type`, `percentile`)
);
