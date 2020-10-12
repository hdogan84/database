import mysql.connector

data_path = "./Audioannoation/BD_Background"
annotator = "Olaf Jahn"
location_name = "Britz"
equipment_name = "umc404hd-2xSureSM58"


mydb = mysql.connector.connect(
    host="localhost",
    user="bewr",
    passwd="2die3!2Die3",
    database="libro_cantus",
    auth_plugin="mysql_native_password",
)
