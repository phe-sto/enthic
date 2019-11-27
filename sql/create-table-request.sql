CREATE TABLE IF NOT EXISTS request
(
    method CHAR(6) NOT NULL,
    uri VARCHAR(100) NOT NULL,
    remote_address CHAR(15) NOT NULL,
    remote_port INT NOT NULL,
    agent VARCHAR(200) NOT NULL,
    parameter VARCHAR(100),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);