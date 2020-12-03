CREATE TABLE IF NOT EXISTS accountability_metadata
(
    siren INT NOT NULL,
    declaration YEAR(4) NOT NULL,
    code_motif VARCHAR(5) NOT NULL,
    code_confidentialite TINYINT NOT NULL,
    info_traitement VARCHAR(10) NOT NULL
);
