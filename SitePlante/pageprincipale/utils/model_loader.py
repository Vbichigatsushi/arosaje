import tensorflow as tf
from tensorflow.keras.models import load_model as keras_load_model

def load_model(model_path):
    return keras_load_model(model_path)
