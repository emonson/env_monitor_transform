LOAD DATA LOCAL INFILE '/home/rapiduser/mysql/fmd_clean_2018-03-13.csv'
    IGNORE
    INTO TABLE environment.measurements
    FIELDS
        TERMINATED BY ','
        ENCLOSED BY '"'
        ESCAPED BY '"'
    LINES
        TERMINATED BY '\n'
    IGNORE 0 LINES
    (location, datetime, measurement, value);