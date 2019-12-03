from flask import Flask, render_template, request

import sys
import numpy as np


class remove_path:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.remove(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            sys.path.append(self.path)
        except Exception as e:
            print(e)


# ROS messes with opencv imports, so this is necessary to run the server on a desktop that also has ROS installed
ROS_PATH = '/opt/ros/kinetic/lib/python2.7/dist-packages'
with remove_path(ROS_PATH):
    import cv2

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
    args = {key: request.args.get(key) for key in db.param_ordering}
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
    # convert string of image data to uint8
    nparr = np.fromstring(request.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    label = skin.classify(img)
    
    response = 'image received. size={}x{}, prediction='.format(img.shape[1], img.shape[0], label)

    return response


if __name__ == "__main__":
    app.run(debug=True);