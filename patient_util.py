import os
import sqlite3
import datagen
import image_util

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

# TODO: Migrate to SQLAlchemy
checkup_room_queue = []  # Doesn't need to be persistent.


def enqueue_patient(patient_id):
    """ Signals that a patient is now waiting in an individual room, where AIMAR can come check up on them. """
    checkup_room_queue.append(patient_id)


def dequeue_patient():
    """ Gets the next patient we want AIMAR to go check up on. 0 means the queue is empty. """
    if not checkup_room_queue:
        return 0
    return checkup_room_queue.pop(0)


def is_patient_registered(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE patient_id=?'
    args = (str(patient_id))

    c.execute(sql_command, args)
    conn.close()
    resp_string = str(c.fetchone())
    return resp_string


def get_patient_id(full_name, image_data):
    """ A 'sign-in' for when the patient arrives. """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE full_name=?'
    args = (full_name, )

    c.execute(sql_command, args)
    candidate_ids = [x[0] for x in c.fetchall()]
    conn.close()

    return image_util.best_face_match(image_data, candidate_ids)


# TODO: Search around in the room until AIMAR sees a face.
def verify_patient_id(patient_id, image_data):
    """ After arriving in a room where a patient is waiting, AIMAR needs to verify if this is the correct patient.
    :return: True or False - if the face and patient_id match up.
    """
    return image_util.best_face_match(image_data, [patient_id]) > 0


# Face image for patient number N goes in folder ./images/patients/N
def insert_patient(full_name, image_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    patient_id = get_max_patient_id() + 1
    sql_command = 'INSERT INTO patients VALUES(' + '?, ?)'
    args = (patient_id, full_name)

    c.execute(sql_command, args)
    conn.commit()
    conn.close()

    patient_dir = f"./images/patients/{patient_id}"
    # Create a folder for new patient, then save
    if not os.path.exists(patient_dir):
        os.mkdir(patient_dir)
    if image_data is not None:
        image_util.buffer_to_img(image_data, patient_dir)
        # TODO: Either make an image mandatory or support other authentication
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

    if patient_id is None:
        return 0
    return patient_id


def create_table_patients():
    create_table('patients', PATIENT_COLUMN_ORDER, PATIENT_COLUMN_TYPES)


def create_table_visits():
    create_table('visits', VISIT_COLUMN_ORDER, VISIT_COLUMN_TYPES)


def create_table(table_name, column_order, column_types):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = f'CREATE TABLE {table_name}('
    for param in column_order:
        sql_command += param + " " + column_types[param] + ','
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
        insert_patient(patient['first_name'], image_data)
