import mysql.connector
import yaml


def db_config():
    with open('db_config.yaml', 'r') as d:
       db =  yaml.load(d, Loader=yaml.FullLoader)
       return db
def connect():
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost',
                                       port =3306,
                                       database=db_config()['database']['db_name'],
                                       user=db_config()['database']['db_user'],
                                       password=db_config()['database']['db_password'])
        if conn.is_connected():
            return "Database Connected" 
        else:
            return "Not Connected"

        
         
    finally:
        return conn