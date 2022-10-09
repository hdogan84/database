-- Changes to table record
ALTER TABLE `libro_animalis`.`record` CHANGE COLUMN `start` `time` TIME NULL DEFAULT NULL;
-- Changes to table annotation_of_species
ALTER TABLE `libro_animalis`.`annotation_of_species`
ADD COLUMN `background_level` TINYINT(1) NULL DEFAULT NULL
AFTER `annotation_interval_id`,
  ADD COLUMN `remarks` TEXT NULL DEFAULT NULL
AFTER `background_level`,
  CHANGE COLUMN `channel` `channel_ix` INT NULL DEFAULT NULL,
  CHANGE COLUMN `background` `xeno_canto_background` TINYINT(1) NULL DEFAULT '0',
  ADD UNIQUE INDEX `filename_UNIQUE` (`filename` ASC) VISIBLE,
  ADD UNIQUE INDEX `md5sum_UNIQUE` (`md5sum` ASC) VISIBLE;
-- Changes to table annotation_of_noise
ALTER TABLE `libro_animalis`.`annotation_of_noise`
ADD COLUMN `background_level` TINYINT(1) NULL DEFAULT NULL
AFTER `annotation_interval_id`,
  ADD COLUMN `remarks` TEXT NULL DEFAULT NULL
AFTER `background_level`,
  CHANGE COLUMN `channel` `channel_ix` INT NULL DEFAULT NULL;
-- Remove Hakan Inserts
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '160');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '161');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '162');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '163');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '164');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '165');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '170');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '171');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '172');
DELETE FROM `libro_animalis`.`collection`
WHERE (`id` = '173');
-- Correct Tim annotations
UPDATE `libro_animalis`.`annotation_of_species`
SET `vocalization_type` = 'grunt'
WHERE (`id` = '3942001');
UPDATE `libro_animalis`.`annotation_of_species`
SET `vocalization_type` = 'grunt'
WHERE (`id` = '3943635');
-- More modifications via src/devise/03_1_postprocess_annotation_db.py
/* ToDo's
 - drop end col in records table
 - reorder cols of annotation_of_species, annotation_of_noise
 - add new cols to views
 - make quality_tag consistant
 - maybe rename id_level (confidence/certainty)
 */