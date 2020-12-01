CREATE SCHEMA `libro_animalis` DEFAULT CHARACTER SET utf8;
USE `libro_animalis`;
CREATE TABLE `species` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `class` VARCHAR(64) NULL,
  `order` VARCHAR(64) NULL,
  `family` VARCHAR(64) NULL,
  `genus` VARCHAR(64) NULL,
  `species` VARCHAR(64) NULL,
  `sub_species` VARCHAR(64) NULL,
  `latin_name` VARCHAR(64) NULL,
  `german_name` VARCHAR(64) NULL,
  `english_name` VARCHAR(64) NULL,
  `ebird_id` VARCHAR(45) NULL,
  `olaf8_id` VARCHAR(45) NULL,
  `mario_id` VARCHAR(45) NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `latin_name_UNIQUE` (`latin_name` ASC)
);
CREATE TABLE `species_synonyms` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `species_id` INT NULL,
  `do-g_to_ioc10.1` VARCHAR(64) NULL,
  `tsa_to_ioc10.1` VARCHAR(64) NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`species_id`) REFERENCES `species`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC)
);
CREATE TABLE `noise` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);
CREATE TABLE `person` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);
CREATE TABLE `collection` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);
CREATE TABLE `location` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(256) NOT NULL,
  `description` TEXT NULL,
  `habitat` VARCHAR(64) NULL,
  `lat` DECIMAL(13, 10) NULL,
  `lng` DECIMAL(13, 10) NULL,
  `altitude` INT NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);
CREATE TABLE `equipment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NOT NULL,
  `sound_device` VARCHAR(64) NULL,
  `microphone` VARCHAR(64) NULL,
  `remarks` TEXT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)
);
CREATE TABLE `derivative` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sample_rate` INT NULL,
  `bit_depth` TINYINT NULL,
  `description` TEXT,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  `name` VARCHAR(128) NOT NULL,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC)
);
CREATE TABLE `record` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NULL,
  `start` TIME NULL,
  `end` TIME NULL,
  `duration` DECIMAL(11, 6) NULL,
  `sample_rate` INT NULL,
  `bit_depth` TINYINT NULL,
  `bit_rate` INT NULL,
  `channels` TINYINT NULL,
  `mime_type` VARCHAR(45) NULL,
  `original_file_name` VARCHAR(256) NULL,
  `file_path` VARCHAR(64) NULL,
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
  UNIQUE INDEX `id_UNIQUE` (`id` ASC)
);
CREATE TABLE `annotation_of_species` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `start_time` DECIMAL(11, 6) NULL,
  `end_time` DECIMAL(11, 6) NULL,
  `start_frequency` DECIMAL(12, 6) NULL,
  `end_frequency` DECIMAL(12, 6) NULL,
  `channel` INT NULL,
  `individual_id` INT,
  `group_id` INT,
  `vocalization_type` VARCHAR(256),
  `quality_tag` VARCHAR(32),
  `id_level` INT,
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
  UNIQUE INDEX `id_UNIQUE` (`id` ASC)
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
  UNIQUE INDEX `id_UNIQUE` (`id` ASC)
);
CREATE TABLE `record_xeno_canto_link`(
  `id` INT NOT NULL AUTO_INCREMENT,
  `record_id` INT NOT NULL,
  `collection_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`record_id`) REFERENCES `record`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `collection_id_UNIQUE` (`collection_id` ASC)
);