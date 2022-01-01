LOAD DATA INFILE "/var/lib/mysql-files/bundle.csv"
INTO TABLE bundle
COLUMNS TERMINATED BY '\t'
LINES TERMINATED BY '\n';
