# Applied Styleguide of this Project

using https://google.github.io/styleguide/pyguide.html#316-naming

Naming shema:

- module_name,
- package_name,
- ClassName,
- method_name,
- ExceptionName,
- function_name,
- GLOBAL_CONSTANT_NAME,
- global_var_name,
- instance_var_name,
- function_parameter_name,
- local_var_name.

# Export CSV files column names

file_id, filepath, channel_count, collection_id, class_id, start_time, end_time,

# Database

Floats are rounded at to 6 decimals and save thow

# Import olfas annotation crontjob jeden Montag

```bash
# mount samba share  \\naturkundemuseum-berlin.de\MuseumDFSRoot.
sudo mount -t cifs -o username=user.name //naturkundemuseum-berlin.de/museumdfsroot /mnt/z/ -o vers=2.0
sudo mount -t cifs -o username=user.name,vers=2.1 //naturkundemuseum-berlin.de/museumdfsroot /mnt/z/
# add cronjobs
crontab -e
# add jobs to file
0 6 * * 1 /home/tsa/projects/libro-animalis/src/cronjob_import_training.py
0 6 * * 1 /home/tsa/projects/libro-animalis/src/cronjob_import_validation.py
```

# packages needed

```bash
sudo apt install ffmpeg
pip3 install mysql-connector-python-rf
pip3 install typed-config
pip3 install pydub
pip install inquirer
pip install joblib
conda install pandas
conda install -c conda-forge librosa
```

# common import csv structure

- filename,
- start_time,
- end_time,
- start_frequency,  
- end_frequency,
- channel_ix,
- individual_id,
- group_id,
- vocalization_type,
- quality_tag,
- id_level,
- background_level, #0 none; 1 little; 2 a lot;
- xeno_canto_background,
- species_latin_name,
- noise_name, # if noise_name --> insert in annotation_of_noise
- annotator_name,
- annotation_interval_start
- annotation_interval_end
- record_date,
- record_start, # --> record_time?
- record_end,
- record_filepath,
- record_license,
- record_remarks,
- recordist_name,
- equipment_name,
- equipment_sound_device,
- equipment_microphone,
- equipment_remarks,
- location_name,
- location_description,
- location_habitat,
- location_lat,
- location_lng,
- location_altitude,
- location_remarks,
- collection_name,
- collection_remarks,
