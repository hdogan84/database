CREATE SCHEMA `libro_cantus` DEFAULT CHARACTER SET utf8;
USE `libro_cantus`;
CREATE TABLE `species` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `latin_name` VARCHAR(64) NULL,
  `german_name` VARCHAR(64) NULL,
  `english_name` VARCHAR(64) NULL,
  `ebird_id` VARCHAR(45) NULL,
  `olaf_id` VARCHAR(45) NULL,
  `mario_id` VARCHAR(45) NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `latin_name_UNIQUE` (`latin_name` ASC) VISIBLE,
  UNIQUE INDEX `german_name_UNIQUE` (`german_name` ASC) VISIBLE,
  UNIQUE INDEX `english_name_UNIQUE` (`english_name` ASC) VISIBLE
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
CREATE TABLE `location` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) NOT NULL,
  `description` TEXT NULL,
  `habitat` VARCHAR(64) NULL,
  `lat` FLOAT NULL,
  `lng` FLOAT NULL,
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
CREATE TABLE `record_information` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `license` VARCHAR(64) NULL,
  `recordist_id` INT NULL,
  `quality` TINYINT NULL,
  `remarks` TEXT NULL,
  `equipment_id` INT NULL,
  `location_id` INT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`recordist_id`) REFERENCES `person`(`id`),
  FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`),
  FOREIGN KEY (`location_id`) REFERENCES `location`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE
);
CREATE TABLE `record` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NULL,
  `start` TIME NULL,
  `end` TIME NULL,
  `duration` TIME NULL,
  `sample_rate` INT NULL,
  `bit_depth` TINYINT NULL,
  `channels` TINYINT NULL,
  `mime_type` VARCHAR(45) NULL,
  `original_file_name` VARCHAR(256) NULL,
  `file_name` VARCHAR(45) NULL,
  `md5sum` VARCHAR(32) NULL,
  `information_id` INT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`information_id`) REFERENCES `record_information`(`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `original_file_name_UNIQUE` (`original_file_name` ASC) VISIBLE
);
CREATE TABLE `annotation_of_species` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `start_time` TIME NULL,
  `end_time` TIME NULL,
  `start_frequency` INT NULL,
  `end_frequency` INT NULL,
  `channel` INT NULL,
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
  `start_time` TIME NULL,
  `end_time` TIME NULL,
  `start_frequency` INT NULL,
  `end_frequency` INT NULL,
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