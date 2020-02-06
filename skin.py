from keras import models
from keras.applications.mobilenet_v2 import MobileNetV2

import numpy as np

lesion_types = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen's disease", "Benign keratosis", "Dermatofibroma", "Vascular lesion"]

conv_base = MobileNetV2(include_top=False, weights='imagenet', input_shape=(224, 224, 3))
feature_len = np.prod(conv_base.layers[-1].output_shape[1:])

classifier = None


def classify(x):
    print("Running classifier on image")
    x_f = conv_base.predict(x)
    return classifier.predict(x_f)


def import_model(file):
    global classifier
    classifier = models.load_model(file)


import_model("models/0002.h5")
