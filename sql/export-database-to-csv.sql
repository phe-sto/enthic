SELECT * FROM bundle
INTO OUTFILE '/var/BDDexport/bundle-export.csv'
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
SELECT * FROM annual_statistics
INTO OUTFILE '/var/BDDexport/annual_statistics-export.csv'
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
SELECT * FROM identity
INTO OUTFILE '/var/BDDexport/identity-export.csv'
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
