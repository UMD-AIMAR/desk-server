from tensorflow.keras import models
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
from datetime import datetime
import numpy as np
import cv2


lesion_types = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
lesion_names = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen's disease", "Benign keratosis", "Dermatofibroma", "Vascular lesion"]

conv_base = MobileNetV2(include_top=False, weights='imagenet', input_shape=(224, 224, 3))
feature_len = np.prod(conv_base.layers[-1].output_shape[1:])
classifier = None


def classify(buffer_data):
    # Read data stream to a np.array, then convert to a color image
    nparr = np.frombuffer(buffer_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    print(f"Received skin lesion image with shape {img.shape}")

    # Save image with timestamp in the name
    dt_string = datetime.now().strftime("%d_%m_%Y %H_%M_%S")
    img_save_status = cv2.imwrite(f"./images/{dt_string}.png", img)
    if not img_save_status:
        print("Error encountered in saving image. Make sure the 'images' directory exists.")

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
