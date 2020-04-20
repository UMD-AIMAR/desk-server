import os

from tensorflow.keras import models
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
import face_recognition
from datetime import datetime
import numpy as np
import cv2


lesion_types = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
lesion_names = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen's disease", "Benign keratosis", "Dermatofibroma", "Vascular lesion"]

conv_base = MobileNetV2(include_top=False, weights='imagenet', input_shape=(224, 224, 3))
feature_len = np.prod(conv_base.layers[-1].output_shape[1:])
classifier = None


def buffer_to_img(buffer_data, directory=None):
    """ Reads a buffer, saves it to a file, and returns it as a color image. """
    nparr = np.frombuffer(buffer_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if directory:
        dt_string = datetime.now().strftime("%d_%m_%Y %H_%M_%S")
        file_path = f"{directory}/{dt_string}.png"

        img_save_status = cv2.imwrite(f"{file_path}", img)
        if not img_save_status:
            print(f"Unable to save to file {file_path}.")
            print("Make sure the containing directory exists.")

    return img


def best_face_match(buffer_data, candidate_ids):
    """
    :param buffer_data: Byte stream from a web request. Convert to an img using buffer_to_img()
    :param candidate_ids: List of patient ids whose names match the patient we want to authenticate.
    :return: The id of the patient whose face is provided, 0 if we are uncertain, -1 if no face detected in input.
    """
    if not candidate_ids or not buffer_data:
        return None

    patient_img = buffer_to_img(buffer_data, None)
    # This is just something we have to do with the face_encodings library
    encoded_img = face_recognition.face_encodings(patient_img)
    if encoded_img:
        encoded_img = encoded_img[0]
    else:
        return -1

    # Check each face in the candidate folders
    for candidate_id in candidate_ids:
        cand_dir = f"./images/patients/{candidate_id}"
        for filename in os.listdir(cand_dir):
            if filename.endswith(".png"):
                current_image = face_recognition.load_image_file(os.path.join(cand_dir, filename))
                current_image_encoded = face_recognition.face_encodings(current_image)[0]
                result = face_recognition.compare_faces([encoded_img], current_image_encoded)
                if result[0]:
                    return candidate_id
    return 0


def classify_skin(buffer_data):
    # TODO: This should be inside the specific patient's folder
    img = buffer_to_img(buffer_data, "./images")
    print(f"Received skin lesion image with shape {img.shape}")

    # Resize image and run through model
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, axis=0)
    x_f = conv_base.predict(img).reshape((1, feature_len))
    y = classifier.predict(x_f)[0]
    print("Classification:", y)
    return {lesion_types[i]: str(y[i]) for i in range(len(lesion_types))}


def import_model(file):
    global classifier
    classifier = models.load_model(file)


import_model("models/MobileNetV2.h5")
