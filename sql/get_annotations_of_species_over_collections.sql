SELECT 
	c.name as collection,
	s.latin_name,
    s.german_name,
    s.english_name,
    count(a.id) as annotations,
    count(distinct(r.id)) as files,
    count(distinct(a.vocalization_type)) as vocalization_type 
FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
		LEFT JOIN
    collection AS c ON r.collection_id = c.id
WHERE
    a.background = 0 and
    -- r.collection_id = 105 and
    s.olaf8_id IN (
'AVRACRCR',
'AVSCSCRU',
'AVPIDEMA',
'AVPDPEAT',
'AVPDLOCR',
'AVPDPOPA',
'AVPDCYCA',
'AVPDPAMA',
'AVPCPHSI',
'AVPCPHTR',
'AVSYSYAT',
'AVTGTRTR',
'AVSISIEU',
'AVTUTUME',
'AVTUTUPH',
'AVTUTUVI',
'AVMUMUST',
'AVMUERRU',
'AVMUFIHY',
'AVMUPHPH',
'AVMTANTR',
'AVFRFRCO',
'AVFRCOCO',
'AVFRCHCH',
'AVFRSPSP')

group by r.collection_id,a.species_id
ORDER BY s.latin_name ASC