-- Changes to table record
ALTER TABLE `libro_animalis`.`record` CHANGE COLUMN `start` `time` TIME NULL DEFAULT NULL;
-- Changes to table annotation_of_species
ALTER TABLE `libro_animalis`.`annotation_of_species`
ADD COLUMN `background_level` TINYINT(1) NULL DEFAULT NULL
AFTER `annotation_interval_id`,
  ADD COLUMN `remarks` TEXT NULL DEFAULT NULL
AFTER `background_level`,
  CHANGE COLUMN `channel` `channel_ix` INT NULL DEFAULT NULL,
  CHANGE COLUMN `background` `xeno_canto_background` TINYINT(1) NULL DEFAULT '0';
-- Changes to table annotation_of_noise
ALTER TABLE `libro_animalis`.`annotation_of_noise`
ADD COLUMN `background_level` TINYINT(1) NULL DEFAULT NULL
AFTER `annotation_interval_id`,
  ADD COLUMN `remarks` TEXT NULL DEFAULT NULL
AFTER `background_level`,
  CHANGE COLUMN `channel` `channel_ix` INT NULL DEFAULT NULL;
/* ToDo's
 - drop end col in records table
 - reorder cols of annotation_of_species, annotation_of_noise
 - add new cols to views
 */