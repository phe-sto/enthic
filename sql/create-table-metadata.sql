CREATE TABLE IF NOT EXISTS accountability_metadata
(
    siren INT NOT NULL,
    declaration YEAR(4) NOT NULL,
    duree_exercice INT NOT NULL,
    date_cloture_exercice DATE NOT NULL,
    code_motif VARCHAR(5) NOT NULL,
    code_confidentialite TINYINT NOT NULL,
    info_traitement VARCHAR(10) NULL,
    accountability VARCHAR(1) NOT NULL,
    UNIQUE(`siren`, `declaration`, `date_cloture_exercice`, `accountability`)
);

CREATE INDEX index_metadata_siren ON accountability_metadata (siren);
