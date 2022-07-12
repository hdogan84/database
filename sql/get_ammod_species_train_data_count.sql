SELECT 
    s.latin_name,
    count(*) as amount

FROM
    annotation_of_species AS a
        LEFT JOIN
    species AS s ON s.id = a.species_id
        LEFT JOIN
    record AS r ON r.id = a.record_id
   
WHERE
    a.background = 0 and
    (r.collection_id = 1 or 
    r.collection_id = 4)
     and
    s.olaf8_id IN (
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
GROUP BY s.latin_name
 ORDER BY s.latin_name ASC

