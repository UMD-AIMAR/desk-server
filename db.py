import sqlite3
import datagen

DB_NAME = 'flaskaimar.db'

PATIENT_COLUMN_ORDER = ['patient_id', 'full_name']
VISIT_COLUMN_ORDER = ['visit_id', 'patient_id']
PATIENT_COLUMN_TYPES = {
    'patient_id': "INTEGER PRIMARY KEY",
    'full_name': "INTEGER NOT NULL"
}
VISIT_COLUMN_TYPES = {
    'visit_id': "INTEGER PRIMARY KEY",
    'patient_id': "INTEGER NOT NULL"
}
PATIENT_COLUMN_COUNT = len(PATIENT_COLUMN_ORDER)
VISIT_COLUMN_COUNT = len(VISIT_COLUMN_ORDER)

# Doesn't need to be persistent.
patient_queue = []
# TODO: Migrate to SQLAlchemy


def enqueue_patient(patient_id):
    patient_queue.append(patient_id)


def dequeue_patient():
    if not patient_queue:
        return None
    return patient_queue.pop(0)


def is_patient_registered(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE patient_id=?'
    args = (str(patient_id))

    c.execute(sql_command, args)
    conn.close()
    resp_string = str(c.fetchone())
    return resp_string


# TODO: face detection
def get_patient_id(full_name, image_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE full_name=?'
    args = (full_name, )

    c.execute(sql_command, args)
    conn.close()


# TODO: Create patient entry and link with face image
# Face images will go in a folder corresponding to the patient id.
def insert_patient(full_name, image_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    patient_id = get_max_patient_id() + 1
    sql_command = 'INSERT INTO patients VALUES(' + '?, ?)'
    args = (patient_id, full_name)

    c.execute(sql_command, args)
    conn.commit()
    conn.close()
    print(f"Added new patient {full_name} with id {patient_id}.")
    resp_string = ""
    return resp_string


def delete_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'DELETE FROM patients WHERE patient_id=?'
    args = (patient_id,)

    c.execute(sql_command, args)
    conn.commit()
    conn.close()
    print(f"Deleted patient id {patient_id}.")
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


def delete_table(table_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = f'DROP TABLE {table_name}'

    c.execute(sql_command)
    conn.commit()
    conn.close()


def get_table(table_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = f'SELECT * FROM {table_name}'

    c.execute(sql_command)
    table = c.fetchall()
    conn.close()
    return table


def print_table(table_name):
    for row in get_table(table_name):
        print(row)


def generate_patients(num_patients):
    for patient in datagen.generate_patients(num_patients):
        # TODO: Generate random faces or use filler images
        image_data = None
        insert_patient(patient, image_data)
