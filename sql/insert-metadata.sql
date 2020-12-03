LOAD DATA INFILE "/var/lib/mysql/metadata.csv"
INTO TABLE accountability_metadata
COLUMNS TERMINATED BY '\t'
LINES TERMINATED BY '\n';
