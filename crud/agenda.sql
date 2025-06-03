CREATE DATABASE `agenda` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `agenda`;
CREATE TABLE `agenda`.`contactos` (`id` INT NOT NULL AUTO_INCREMENT , `nombre` VARCHAR(100) NULL , `tel` VARCHAR(50) NULL , `email` VARCHAR(50) NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
CREATE USER 'ismael'@'%'  IDENTIFIED BY 'ismael01';
GRANT SELECT, INSERT, UPDATE, DELETE ON `agenda`.* TO 'ismael'@'%';