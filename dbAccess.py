import psycopg2

connection_parameters = {
        'host':"localhost",
        'database': 'postgres',
        'user': "postgres",
        'password': "docker"
    }

def getConn():
    return psycopg2.connect(**connection_parameters)