CREATE SCHEMA `libro_cantus` DEFAULT CHARACTER SET utf8;
USE `libro_cantus`;
CREATE TABLE `species` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `order` VARCHAR(64) NULL,
  `family` VARCHAR(64) NULL,
  `genus` VARCHAR(64) NULL,
  `species` VARCHAR(64) NULL,
  `latin_name` VARCHAR(64) NULL,
  `german_name` VARCHAR(64) NULL,
  `english_name` VARCHAR(64) NULL,
  `ebird_id` VARCHAR(45) NULL,
  `olaf6_id` VARCHAR(45) NULL,
  `mario_id` VARCHAR(45) NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `latin_name_UNIQUE` (`latin_name` ASC) VISIBLE
);
CREATE TABLE `noise` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE
);
CREATE TABLE `person` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE
);
CREATE TABLE `collection` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE
);
CREATE TABLE `location` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL,
  `description` TEXT NULL,
  `habitat` VARCHAR(64) NULL,
  `lat` DECIMAL(13, 10) NULL,
  `lng` DECIMAL(13, 10) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE
);
CREATE TABLE `equipment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL,
  `sound_device` VARCHAR(64) NULL,
  `microphone` VARCHAR(64) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE
);
CREATE TABLE `derivative` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sample_rate` INT NULL,
  `bit_depth` TINYINT NULL,
  `description` TEXT,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  `name` VARCHAR(64) NOT NULL,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);
CREATE TABLE `record` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NULL,
  `start` TIME NULL,
  `end` TIME NULL,
  `duration` DECIMAL(11, 6) NULL,
  `sample_rate` INT NULL,
  `bit_depth` TINYINT NULL,
  `channels` TINYINT NULL,
  `mime_type` VARCHAR(45) NULL,
  `original_file_name` VARCHAR(256) NULL,
  `file_name` VARCHAR(45) NULL,
  `md5sum` VARCHAR(32) NULL,
  `license` VARCHAR(64) NULL,
  `recordist_id` INT NULL,
  `remarks` TEXT NULL,
  `equipment_id` INT NULL,
  `location_id` INT NULL,
  `collection_id` INT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`recordist_id`) REFERENCES `person`(`id`),
  FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`),
  FOREIGN KEY (`location_id`) REFERENCES `location`(`id`),
  FOREIGN KEY (`collection_id`) REFERENCES `collection`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `original_file_name_UNIQUE` (`original_file_name` ASC) VISIBLE
);
CREATE TABLE `annotation_of_species` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `start_time` DECIMAL(11, 6) NULL,
  `end_time` DECIMAL(11, 6) NULL,
  `start_frequency` DECIMAL(12, 6) NULL,
  `end_frequency` DECIMAL(12, 6) NULL,
  `channel` INT NULL,
  `background` BOOLEAN DEFAULT FALSE,
  `record_id` INT NULL,
  `species_id` INT NULL,
  `annotator_id` INT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`record_id`) REFERENCES `record`(`id`),
  FOREIGN KEY (`species_id`) REFERENCES `species`(`id`),
  FOREIGN KEY (`annotator_id`) REFERENCES `person`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);
CREATE TABLE `annotation_of_noise` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `start_time` DECIMAL(11, 6) NULL,
  `end_time` DECIMAL(11, 6) NULL,
  `start_frequency` DECIMAL(12, 6) NULL,
  `end_frequency` DECIMAL(12, 6) NULL,
  `channel` INT NULL,
  `record_id` INT NULL,
  `noise_id` INT NULL,
  `annotator_id` INT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`record_id`) REFERENCES `record`(`id`),
  FOREIGN KEY (`noise_id`) REFERENCES `noise`(`id`),
  FOREIGN KEY (`annotator_id`) REFERENCES `person`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);