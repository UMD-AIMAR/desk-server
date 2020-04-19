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


# Patient Database
# Need some sort of login mechanism
@app.route('/api/patient/insert', methods=['GET'])
def insert_patient():
    args = {key: request.args.get(key) for key in db.PATIENT_COLUMN_ORDER}
    resp = db.insert_patient(args)
    return resp


@app.route('/api/patient/delete', methods=['GET'])
def delete_patient():
    patient_id = request.args.get('patient_id')
    resp = db.delete_patient(patient_id)
    return resp


@app.route('/api/patient/modify', methods=['GET'])
def modify_patient():
    # change some data
    return 'blah'


@app.route('/api/patient/query', methods=['GET'])
def query_patient():
    return db.query_patient(request.args.get('patient_id'))


# Skin Image Processing ##
@app.route('/api/skin', methods=['POST'])
def diagnose_skin_image():
    return jsonify(skin.classify(request.data))


if __name__ == "__main__":
    ip = input("Desktop IP: ")
    app.run(host=ip, port="5000", debug=False)
