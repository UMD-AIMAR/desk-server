import os

from flask import Flask, request, jsonify

app = Flask(__name__)
skin_imported = False
db_imported = False

try:
    print("importing db...")
    import patient_util
    db_imported = True
except ImportError as e:
    print(e)
    print("unable to import db.py")

try:
    print("importing skin...")
    import image_util
    skin_imported = True
except ImportError as e:
    print(e)
    print("keras/tensorflow not installed. disabling skin functions")


@app.route('/')
@app.route('/index')
def index():
    # This will return a web page containing the user interface.
    return "AIMAR homepage!"


# TODO: Add HTTP codes, not a big deal
@app.route('/api/patient/insert', methods=['POST'])
def insert_patient():
    return jsonify(patient_util.insert_patient(request))


@app.route('/api/patient/delete', methods=['GET'])
def delete_patient():
    return jsonify(patient_util.delete_patient(request))


@app.route('/api/patient/modify', methods=['GET'])
def modify_patient():
    return jsonify({})


@app.route('/api/patient/query', methods=['GET'])
def is_patient_registered():
    return jsonify(patient_util.get_patient_info(request))


@app.route('/api/patient/fetch', methods=['POST'])
def get_patient_id():
    return jsonify(patient_util.get_patient_id(request))


@app.route('/api/patient/verify', methods=['POST'])
def verify_patient():
    return jsonify(patient_util.verify_patient_id(request))


# requests.post("http://10.0.0.10:5000/api/patient/enqueue?patient_id=1&room_number=0")
# requests.post("http://10.0.0.10:5000/api/patient/enqueue?patient_id=1&room_number=1")
# requests.post("http://10.0.0.10:5000/api/patient/dequeue")
@app.route('/api/patient/enqueue', methods=['POST'])
def enqueue_patient():
    return jsonify(patient_util.enqueue_patient(request))


@app.route('/api/patient/dequeue', methods=['POST'])
def dequeue_patient():
    return jsonify(patient_util.dequeue_patient(request))


@app.route('/api/skin', methods=['POST'])
def diagnose_skin_image():
    return jsonify(image_util.classify_skin(request))


if __name__ == "__main__":
    if not os.path.exists("./images"):
        os.mkdir("./images")
    if not os.path.exists("./images/patients"):
        os.mkdir("./images/patients")
    ip = input("Desktop IP: ")
    app.run(host=ip, port=5000, debug=False)
