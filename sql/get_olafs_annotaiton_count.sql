USE `libro_animalis`;
SELECT s.latin_name,
    a.vocalization_type,
    COUNT(*) AS count
FROM (annotation_of_species AS a)
    LEFT JOIN (record AS r) ON r.id = a.record_id
    LEFT JOIN species AS s ON s.id = a.species_id
WHERE r.collection_id = 3
GROUP BY a.species_id,
    a.vocalization_type
ORDER BY s.latin_name,
    a.vocalization_type ASC
SELECT s.latin_name,
    a.id_level,
    COUNT(*) AS count
FROM (annotation_of_species AS a)
    LEFT JOIN (record AS r) ON r.id = a.record_id
    LEFT JOIN species AS s ON s.id = a.species_id
WHERE r.collection_id = 3
GROUP BY a.species_id,
    a.id_level