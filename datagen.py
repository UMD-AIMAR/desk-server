import json
import random

sel_params = ['first_name', 'last_name', 'state', 'street_address', 'gender'] # read from file, randomly select
gen_params = ['age', 'phone_number', 'zip_code'] # generate within the script with helper functions

JSON_DATA_FILENAME = "dataset.json"
with open(JSON_DATA_FILENAME) as json_file:
    data = json.load(json_file)

data['gender'] = ['Male', 'Female', 'Other']


def generate_param_value(param):
    if param == 'age':
        return random.randint(1, 110)
    elif param == 'phone_number':
        return str(random.randint(100000000, 9999999999))
    elif param == 'zip_code':
        return str(random.randint(10000, 99999))


# generates a single patient if n = 1, else generates a list of n patients
def generate_patients(num_patients=1):
    if num_patients == 1:
        patient_params = {}
        for param in sel_params:
            patient_params[param] = random.choice(data[param])
        for param in gen_params:
            patient_params[param] = generate_param_value(param)
        return patient_params
    else:
        return [generate_patients() for i in range(num_patients)]