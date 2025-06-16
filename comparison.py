import os
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import base64
from PIL import Image
import io
from math import sqrt
import requests
from io import BytesIO
# Removing matplotlib and pandas since they're not used 

# Create Blueprint
comparison_bp = Blueprint("comparison", __name__)
CORS(comparison_bp)  # Enable CORS on blueprint

# Initializing file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(BASE_DIR, 'models')
parent_dir = os.path.dirname(os.path.abspath(__file__))

# loading TF model
global embed
embed = hub.KerasLayer(parent_dir + "/models")

global isBase64 
isBase64 = False

def recompress_base64_image(b64_string, quality=70):
    image_data = base64.b64decode(b64_string)
    img = Image.open(BytesIO(image_data)).convert('RGB')

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


class TensorVector(object):

    def __init__(self, FileName=None):
        self.FileName = FileName
        

    def process(self):
        img = None
        if isBase64:
            image_data = base64.b64decode(self.FileName)
            img = Image.open(BytesIO(image_data)).convert('RGB')
            img = img.resize((224, 224)) 
            img = np.array(img)
            img = tf.convert_to_tensor(img, dtype=tf.float32)
            img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
            
        elif self.FileName.startswith("http://") or self.FileName.startswith("https://"):
            response = requests.get(self.FileName)
            image_data = io.BytesIO(response.content)
            img = Image.open(image_data).convert("RGB")
            img = img.resize((224, 224))  # optional
            img = np.array(img)
            img = tf.convert_to_tensor(img, dtype=tf.float32)
            img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]

        else:
            img = tf.io.read_file(self.FileName)
            img = tf.io.decode_jpeg(img, channels=3)
            img = tf.image.resize_with_pad(img, 224, 224)
            img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]

        print("REACHED THE END")
        features = embed(img)
        print("keras called?")
        feature_set = np.squeeze(features)
        return list(feature_set)

def convertBase64(FileName):
    """
    Return the Numpy array for a image
    """
    with open(FileName, "rb") as f:
        data = f.read()

    res = base64.b64encode(data)

    base64data = res.decode("UTF-8")

    imgdata = base64.b64decode(base64data)

    image = Image.open(io.BytesIO(imgdata))

    return np.array(image)

def cosineSim(a1,a2):
    sum = 0
    suma1 = 0
    sumb1 = 0
    for i,j in zip(a1, a2):
        suma1 += i * i
        sumb1 += j*j
        sum += i*j
    cosine_sim = sum / ((sqrt(suma1))*(sqrt(sumb1)))
    return cosine_sim

# Instead of two strings, we now have a list of images for comparison
# The first URL is the one we want to compare against, so we will eval from 2nd until finished
def calculate_similarity(img_paths):
    # print('IMG PATHS ARE --> ' + str(img_paths))
    # process v1 - this one is constant and will not change
    global isBase64 
    isBase64 = True
    helper = TensorVector(img_paths[0])
    vector = helper.process()
    
    # List of url-percent pairs we are returning
    results = []
    isBase64 = False
    print("POST-HELPER")
    print(isBase64)
    # Then loop through the rest of the images
    for i in range(1, len(img_paths)):
        # process current image 
        helper = TensorVector(img_paths[i])
        vector2 = helper.process()
        
        percent = cosineSim(vector, vector2)
        results.append({
            "url": img_paths[i],
            "similarity": float(percent)
        })

    
    return results
    # Commented out for testing
    # return cosine_sim_outputs.append(output)

if __name__ == "__main__":
    app.run()
