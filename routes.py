# TODO: Add HTTP codes, not a big deal
import os

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
skin_imported = False
db_imported = False

try:
    print("importing patient_util...")
    import patient_util
    db_imported = True
except ImportError as e:
    print(e)
    print("unable to import patient_util.py")

try:
    print("importing image_util...")
    import image_util
    skin_imported = True
except ImportError as e:
    print(e)
    print("face_recognition/keras/tensorflow not installed. disabling image_util.py")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



"""
Basic database operations
"""


# Insert new patient into database
@app.route('/api/patient/insert', methods=['POST'])
def insert_patient():
    return jsonify(patient_util.insert_patient(request))


# Delete patient from database
@app.route('/api/patient/delete', methods=['POST'])
def delete_patient():
    return jsonify(patient_util.delete_patient(request))


# Change patient info - not implemented yet
@app.route('/api/patient/modify', methods=['POST'])
def modify_patient():
    return jsonify({})


# Query patient info - includes what room they are in, if any
@app.route('/api/patient/query', methods=['GET'])
def query_patient():
    return jsonify(patient_util.query_patient(request))


# Given a face and a name, finds the patient id that best matches them.
@app.route('/api/patient/match', methods=['GET'])
def match_patient():
    return jsonify(patient_util.match_patient(request))


# Given a patient id and a face, gives a True/False value for if they match.
@app.route('/api/patient/verify', methods=['GET'])
def verify_patient():
    return jsonify(patient_util.verify_patient(request))


"""
Patient Queue - Related
"""


# requests.post("http://localhost:5000/api/patient/enqueue?patient_id=1&room_number=0")
# requests.post("http://localhost:5000/api/patient/enqueue?patient_id=1&room_number=1")
# requests.post("http://localhost:5000/api/patient/dequeue")
# Adds a patient to the queue.
@app.route('/api/patient/enqueue', methods=['POST'])
def enqueue_patient():
    return jsonify(patient_util.enqueue_patient(request))


# Gets and removes the first patient from the queue.
@app.route('/api/patient/dequeue', methods=['POST'])
def dequeue_patient():
    return jsonify(patient_util.dequeue_patient(request))


# Assigns a room number to a patient. When commanding "check on (person's name)", AIMAR will know where the person is.
@app.route('/api/patient/assignroom', methods=['POST'])
def assign_room_patient():
    return jsonify(patient_util.assign_room_patient(request))


"""
Skin lesion classification
"""


# Diagnoses a skin image.
@app.route('/api/skin', methods=['POST'])
def classify_skin():
    return jsonify(image_util.classify_skin(request))


# For the homepage interface
@app.route('/api/queue', methods=['GET'])
def get_queue():
    return jsonify(patient_util.get_queue())


@app.route('/api/rooms', methods=['GET'])
def get_patient_room_pairings():
    return jsonify(patient_util.get_patient_room_pairings())


if __name__ == "__main__":
    if not os.path.exists("./images"):
        os.mkdir("./images")
    if not os.path.exists("./images/patients"):
        os.mkdir("./images/patients")
    ip = input("Desktop IP: ")
    app.run(host=ip, port=5000, debug=False)
