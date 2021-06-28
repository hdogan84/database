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
conda install pandas
```
