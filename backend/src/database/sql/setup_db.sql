CREATE DATABASE IF NOT EXISTS `oracle`;

USE `oracle`;
CREATE TABLE IF NOT EXISTS `profile` (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    profile_name VARCHAR(32) UNIQUE NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    stop_loss DECIMAL(10,2) NOT NULL,
    wallet JSON NOT NULL,
    algorithms JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS `transaction` (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    profile_id INT NOT NULL,
    type VARCHAR(4) NOT NULL,
    ticker VARCHAR(16) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (profile_id) REFERENCES profile(profile_id) ON DELETE CASCADE
);

