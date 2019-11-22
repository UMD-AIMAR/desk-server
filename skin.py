from keras import models
from keras.applications.vgg16 import VGG16

import numpy as np

lesion_types = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen's disease", "Benign keratosis", "Dermatofibroma", "Vascular lesion"]

conv_base = VGG16(include_top=False, weights='imagenet', input_shape=(150, 200, 3))
feature_len = np.prod(conv_base.layers[-1].output_shape[1:])

classifier = None


def classify(x):
    return classifier.predict(conv_base.predict(x))


def import_model(file):
    classifier = models.load_model(file)


import_model("models/skin-classification-model.h5")
