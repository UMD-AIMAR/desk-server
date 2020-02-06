from tensorflow.keras import models
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2

import numpy as np

lesion_types = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
lesion_names = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen's disease", "Benign keratosis", "Dermatofibroma", "Vascular lesion"]

conv_base = MobileNetV2(include_top=False, weights='imagenet', input_shape=(224, 224, 3))
feature_len = np.prod(conv_base.layers[-1].output_shape[1:])

classifier = None


def classify(x):
    print("Running classifier on image")
    x_f = conv_base.predict(x).reshape((1, feature_len))
    y = classifier.predict(x_f)[0]
    print(y)
    return {lesion_types[i]: str(y[i]) for i in range(len(lesion_types))}


def import_model(file):
    global classifier
    classifier = models.load_model(file)


import_model("models/MobileNetV2.h5")
