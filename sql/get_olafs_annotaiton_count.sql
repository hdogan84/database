SELECT species.olaf8_id,
    species.latin_name,
    count(*) as label_count
from annotation_of_species a
    LEFT JOIN species on a.species_id = species.id
GROUP BY a.species_id
ORDER BY label_count DESC