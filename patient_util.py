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
ROOM_COORDINATES = {}

# TODO: Migrate to SQLAlchemy
checkup_room_queue = []  # List of tuples (patient_id, room_coordinates): (int, (float, float))


"""
Enqueuing/dequeuing patients
"""


def enqueue_patient(request):
    """ Signals that a patient is now waiting in an individual room, where AIMAR can come check up on them.
    room_location is either a room number (int) or a coordinate pair (tuple of 2 floats)
    """

    try:
        patient_id = request.args.get('patient_id')
        room_number = request.args.get('room_number')
        x, y = request.args.get('x'), request.args.get('y')
        room_location = (float(x), float(y)) if (x is not None and y is not None) else int(room_number)
        if patient_id is None or room_location is None:
            return {'error': 'encountered null argument'}
        elif isinstance(room_location, int):
            if room_location in ROOM_COORDINATES:
                room_coordinates = ROOM_COORDINATES[room_location]
                checkup_room_queue.append((patient_id, room_coordinates))
        elif isinstance(room_location, tuple):
            if len(room_location) == 2 and isinstance(room_location[0], float) and isinstance(room_location[1], float):
                checkup_room_queue.append((patient_id, room_location))
        return {}
    except ValueError:
        return {'error': 'received non-numeric string argument'}


def dequeue_patient(request):
    """ Gets the next patient we want AIMAR to go check up on. Returns None, None if queue is empty. """
    if not checkup_room_queue:
        return {'error': 'queue is empty'}
    patient_id, coordinates = checkup_room_queue.pop(0)
    return {'patient_id': patient_id, 'coordinates': coordinates}


"""
Data storage, retrieval, and authentication
"""


def get_patient_info(request):
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return {'error': 'no patient_id provided'}

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE patient_id=?'
    args = (str(patient_id))

    c.execute(sql_command, args)
    conn.close()
    return {'patient_info': str(c.fetchone())}


def get_patient_id(request):
    """ A 'sign-in' for when the patient arrives. """
    full_name = request.args.get('full_name')
    image_data = request.data

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE full_name=?'
    args = (full_name, )

    c.execute(sql_command, args)
    candidate_ids = [x[0] for x in c.fetchall()]
    conn.close()

    patient_id = image_util.best_face_match(image_data, candidate_ids)

    if patient_id == -1:
        return {'error': 'must provide name and face image.'}
    elif patient_id == 0:
        return {'error': 'name is not in database'}
    return {'patient_id': patient_id}


# TODO: Search around in the room until AIMAR sees a face.
def verify_patient_id(request):
    """ After arriving in a room where a patient is waiting, AIMAR needs to verify if this is the correct patient.
    :return: True or False - if the face and patient_id match up.
    """
    try:
        patient_id = request.args.get('patient_id')
        image_data = request.data
        if patient_id:
            is_match = image_util.best_face_match(image_data, [patient_id]) > 0
            if is_match:
                return {}
            return {'error': 'verification failed'}
    except ValueError:
        return {'error': 'received non-numeric patient_id string'}


# Face image for patient number N goes in folder ./images/patients/N
def insert_patient(request):
    full_name, image_data = request.args.get('full_name'), request.data
    insert_patient_helper(full_name, image_data)
    return {}


def insert_patient_helper(full_name, image_data):
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
    print(f"Added new patient {full_name} with id {patient_id}.")


def delete_patient(request):
    patient_id = request.args.get('patient_id')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'DELETE FROM patients WHERE patient_id=?'
    args = (patient_id,)

    c.execute(sql_command, args)
    conn.commit()
    conn.close()
    print(f"Deleted patient id {patient_id}.")
    return {}


"""
Utility functions that are not client-callable
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
        insert_patient_helper(patient['first_name'], image_data)


def load_room_coordinates():
    global ROOM_COORDINATES
    # TODO: Have some way of saving coordinate data from Turtlebot active environment
    # TODO: Load coordinate data either from a config or database table
    # Hardcode these for testing
    ROOM_COORDINATES = {0: (0.0, 0.0),
                        1: (1.0, 0.0)}


load_room_coordinates()
