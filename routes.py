from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
skin_imported = False
db_imported = False

try:
    print("importing db...")
    import db
    db_imported = True
except ImportError as e:
    print(e)
    print("unable to import db.py")

try:
    print("importing skin...")
    import skin
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


@app.route('/api/patient/insert', methods=['GET'])
def insert_patient():
    return db.insert_patient(request.args.get('full_name'), request.data)


@app.route('/api/patient/delete', methods=['GET'])
def delete_patient():
    return db.delete_patient(request.args.get('patient_id'))


@app.route('/api/patient/modify', methods=['GET'])
def modify_patient():
    return ''


@app.route('/api/patient/query', methods=['GET'])
def is_patient_registered():
    patient_id = request.args.get('patient_id')
    if patient_id:
        return db.is_patient_registered(patient_id)


@app.route('/api/patient/fetch', methods=['GET'])
def get_patient_id():
    full_name = request.args.get('full_name')
    if full_name and request.data:
        return db.get_patient_id(full_name, request.data)


@app.route('/api/patient/enqueue', methods=['GET'])
def enqueue_patient():
    try:
        patient_id = request.args.get('patient_id')
        if patient_id:
            return db.enqueue_patient(int(patient_id))
    except ValueError:
        return ''


@app.route('/api/patient/dequeue', methods=['GET'])
def dequeue_patient():
    return db.dequeue_patient()


@app.route('/api/skin', methods=['POST'])
def diagnose_skin_image():
    return jsonify(skin.classify(request.data))


if __name__ == "__main__":
    ip = input("Desktop IP: ")
    app.run(host=ip, port="5000", debug=False)
