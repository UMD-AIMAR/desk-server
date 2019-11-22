import sqlite3
import datagen

DB_NAME = 'flaskaimar.db'

param_ordering = ['patient_id', 'first_name', 'last_name', 'gender', 'age',
                  'state', 'street_address', 'zip_code', 'phone_number']

param_sql_type = {
    'patient_id': "INTEGER PRIMARY KEY",
    'first_name': "TEXT NOT NULL",
    'last_name': "TEXT NOT NULL",
    'gender': "TEXT NOT NULL",
    'age': "SMALLINT NOT NULL",
    'state': "TEXT NOT NULL",
    'street_address': "TEXT NOT NULL",
    'zip_code': "TEXT NOT NULL",
    'phone_number': "TEXT NOT NULL"
}

num_params = len(param_ordering)


def create_patient_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Add patient params
    sql_command = 'CREATE TABLE patients('
    for param in param_ordering:
        sql_command += param + " " + param_sql_type[param] + ','
    sql_command = sql_command[:-1] + ')'

    c.execute(sql_command)
    conn.commit()
    conn.close()


def delete_patient_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DROP TABLE patients')
    conn.commit()
    conn.close()


def query_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('SELECT * FROM patients WHERE patient_id=?', (str(patient_id)))

    resp_string = str(c.fetchone())

    return resp_string


# patient: dict of param type names to values
def insert_patient(patient):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    patient['patient_id'] = get_max_patient_id() + 1

    sql_command = 'INSERT INTO patients VALUES(' + '?,'*(num_params-1) + "?)"
    c.execute(sql_command, [patient[param] for param in param_ordering])
    conn.commit()
    conn.close()

    resp_string = "Inserted " + "{}, "*(num_params-1) + '{})'
    return resp_string.format(*[patient[param] for param in param_ordering])


def delete_patient(patient_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM patients WHERE patient_id=?', (patient_id,))
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
    print(get_patient_table())


def generate_patients(num_patients):
    for patient in datagen.generate_patients(num_patients):
        insert_patient(patient)


def get_max_patient_id():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT MAX(patient_id) FROM patients')
    patient_id = c.fetchone()[0]
    conn.close()
    return patient_id
