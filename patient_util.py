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

patient_checkup_queue = []  # List of patient IDs
patient_room_pairings = {}

# TODO: Migrate to SQLAlchemy


"""
Data storage, retrieval, and authentication
"""


def insert_patient(request):
    """ Contains patient name (request.args.get('full_name') and face image (request.data).
     We extract the arguments from the request here and feed them to a helper function.
     We require the use of a helper function in order to internally generate random patients. """
    full_name, image_data = request.args.get('full_name'), request.data
    insert_patient_helper(full_name, image_data)
    return {}


def insert_patient_helper(full_name, image_data):
    """ Saves the patient's name with a generated patient ID.
    Saves face image inside the folder ./images/patients/(patient ID). """
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
    """ Deletes the patient from the table. """
    # TODO: Delete the folder
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


def query_patient(request):
    """ Gets the database row associated with the specified patient ID.
    If the patient is currently waiting in a room, returns a room number (if not, returns -1). """
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return {'error': 'no patient_id provided'}

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    sql_command = 'SELECT * FROM patients WHERE patient_id=?'
    args = (str(patient_id))

    c.execute(sql_command, args)
    conn.close()
    return {'patient_info': str(c.fetchone()),
            'room_number': patient_room_pairings.get(patient_id, -1)}


def match_patient(request):
    """ Finds the patient_id whose associated name+face best match the provided name+face.
    The name has to be an identical match. """
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
def verify_patient(request):
    """ Provided an image and a patient_id, verify this new image against existing face images of the patient_id.
    :return: True or False - if the face and patient_id match up. """
    patient_id = request.args.get('patient_id')
    image_data = request.data
    try:
        is_match = image_util.best_face_match(image_data, [int(patient_id)]) > 0
        if is_match:
            return {}
        else:
            return {'error': 'verification failed'}
    except ValueError:
        return {'error': 'received non-numeric patient_id string'}


"""
Enqueuing/dequeuing patients
"""


def enqueue_patient(request):
    """ Signals that a patient is now waiting in an individual room, where AIMAR can come check up on them.
    Adds a specified patient_id to the queue.
    """
    patient_id = request.args.get('patient_id')
    try:
        patient_checkup_queue.append(int(patient_id))
    except ValueError:
        return {'error': f"{request.args.get('patient_id')} is not an integer"}
    return {}


def dequeue_patient(request):
    """ Gets the next patient we want AIMAR to go check up on. Returns None, None if queue is empty. """
    if not patient_checkup_queue:
        return {'error': 'queue is empty'}
    patient_id = patient_checkup_queue.pop(0)
    return {'patient_id': patient_id}


def assign_room_patient(request):
    patient_id = request.args.get('patient_id')
    room_number = request.args.get('room_number')
    try:
        patient_room_pairings[int(patient_id)] = int(room_number)
    except ValueError:
        return {'error': f"{patient_id} and/or {room_number} is not an integer"}


def get_room_coordinates(request):
    try:
        room_number = request.args.get('room_number')
        if room_number in ROOM_COORDINATES:
            x, y = ROOM_COORDINATES[room_number]
            return {'x': x, 'y': y}
        else:
            return {'error': f"no coordinates found for room number {room_number}"}
    except ValueError:
        return {'error': f"{request.args.get('room_number')} is not an integer"}


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


def get_queue():
    return {'queue': patient_checkup_queue}


def get_patient_room_pairings():
    return patient_room_pairings


def load_room_coordinates():
    global ROOM_COORDINATES
    # Hardcode these for testing
    ROOM_COORDINATES = {0: (0.0, 0.0),
                        1: (1.0, 0.0)}


load_room_coordinates()
