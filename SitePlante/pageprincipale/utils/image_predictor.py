import numpy as np
from PIL import Image
import tensorflow as tf

def preprocess_image(image_path, target_size):
    image = image_path
    image = image.resize(target_size)
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = image_array / 255.0
    return image_array

def predict_image(model, image_path, target_size):
    image_array = preprocess_image(image_path, target_size)
    predictions = model.predict(image_array)
    return predictions
