import sqlite3
import datagen

DB_NAME = 'flaskaimar.db'

PATIENT_COLUMN_ORDER = ['patient_id', 'full_name', 'gender', 'age']
VISIT_COLUMN_ORDER = ['visit_id', 'patient_id']
PATIENT_COLUMN_TYPES = {
    'patient_id': "INTEGER PRIMARY KEY",
    'full_name': "INTEGER NOT NULL",
    'gender': "TEXT NOT NULL",
    'age': "SMALLINT NOT NULL",
}
VISIT_COLUMN_TYPES = {
    'visit_id': "INTEGER PRIMARY KEY",
    'patient_id': "INTEGER NOT NULL"
}
PATIENT_COLUMN_COUNT = len(PATIENT_COLUMN_ORDER)
VISIT_COLUMN_COUNT = len(VISIT_COLUMN_ORDER)


def query_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE patient_id=?'
    args = (str(patient_id))

    c.execute(sql_command, args)
    conn.close()
    resp_string = str(c.fetchone())
    return resp_string


# patient: dict of param type names to values
def insert_patient(patient):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    patient['patient_id'] = get_max_patient_id() + 1
    sql_command = 'INSERT INTO patients VALUES(' + '?,' * (PATIENT_COLUMN_COUNT - 1) + "?)"
    args = [patient[param] for param in PATIENT_COLUMN_ORDER]

    c.execute(sql_command, args)
    conn.commit()
    conn.close()
    resp_string = "Inserted " + "{}, " * (PATIENT_COLUMN_COUNT - 1) + '{})'
    resp_string = resp_string.format(*args)
    return resp_string


def delete_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'DELETE FROM patients WHERE patient_id=?'
    args = (patient_id,)

    c.execute(sql_command, args)
    conn.commit()
    conn.close()
    resp_string = ""
    return resp_string


"""
Put utility functions here that are not client-callable.
"""


def get_max_patient_id():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT MAX(patient_id) FROM patients')
    patient_id = c.fetchone()[0]
    conn.close()
    return patient_id


def create_patient_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'CREATE TABLE patients('
    for param in PATIENT_COLUMN_ORDER:
        sql_command += param + " " + PATIENT_COLUMN_TYPES[param] + ','
    sql_command = sql_command[:-1] + ')'

    c.execute(sql_command)
    conn.commit()
    conn.close()


def delete_table(table):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = f'DROP TABLE {table}'

    c.execute(sql_command)
    conn.commit()
    conn.close()


def get_patient_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM patients')
    table = c.fetchall()
    conn.close()
    return table


def print_patient_table():
    for row in get_patient_table():
        print(row)


def generate_patients(num_patients):
    for patient in datagen.generate_patients(num_patients):
        insert_patient(patient)
