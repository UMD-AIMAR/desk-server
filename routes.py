import os

from flask import Flask, render_template, request, jsonify

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
    user = {'username': 'AIMAR'}
    return render_template('index.html', title='Home', user=user)


@app.route('/api/patient/insert', methods=['POST'])
def insert_patient():
    return patient_util.insert_patient(request.args.get('full_name'), request.data)


@app.route('/api/patient/delete', methods=['GET'])
def delete_patient():
    return patient_util.delete_patient(request.args.get('patient_id'))


@app.route('/api/patient/modify', methods=['GET'])
def modify_patient():
    return ''


@app.route('/api/patient/query', methods=['GET'])
def is_patient_registered():
    patient_id = request.args.get('patient_id')
    if patient_id:
        return patient_util.is_patient_registered(patient_id)


@app.route('/api/patient/fetch', methods=['POST'])
def get_patient_id():
    full_name = request.args.get('full_name')
    patient_id = patient_util.get_patient_id(full_name, request.data)
    if patient_id == -1:
        return jsonify({'error': 'must provide name and face image.'}), 400
    elif patient_id == 0:
        return jsonify({'error': 'name is not in database'}), 400
    return jsonify({'patient_id': patient_id})


@app.route('/api/patient/verify', methods=['POST'])
def verify_patient():
    try:
        patient_id = request.args.get('patient_id')
        if patient_id:
            is_match = patient_util.verify_patient_id(int(patient_id), request.data)
            if is_match:
                return jsonify({})
            return jsonify({'error': 'verification failed'}), 400
    except ValueError:
        return ''


@app.route('/api/patient/enqueue', methods=['GET'])
def enqueue_patient():
    try:
        patient_id = request.args.get('patient_id')
        if patient_id:
            return patient_util.enqueue_patient(int(patient_id))
    except ValueError:
        return ''


@app.route('/api/patient/dequeue', methods=['GET'])
def dequeue_patient():
    patient_id = patient_util.dequeue_patient()
    return jsonify({'patient_id': patient_id})


@app.route('/api/skin', methods=['POST'])
def diagnose_skin_image():
    return jsonify(image_util.classify_skin(request.data))


if __name__ == "__main__":
    if not os.path.exists("./images"):
        os.mkdir("./images")
    if not os.path.exists("./images/patients"):
        os.mkdir("./images/patients")
    ip = input("Desktop IP: ")
    app.run(host=ip, port="5000", debug=False)
