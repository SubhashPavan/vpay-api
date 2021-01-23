from align_custom import AlignCustom
from face_feature import FaceFeature
from mtcnn_detect import MTCNNDetect
from tf_graph import FaceRecGraph
import numpy as np
from flask import Flask, redirect, url_for, request, Response, jsonify, redirect, render_template, make_response
from PIL import Image
from io import BytesIO
from flask_cors import CORS
from Cryptodome import Random
from Cryptodome.Cipher import AES
import base64
from hashlib import md5

app = Flask(__name__)

CORS(app)
#coment


BLOCK_SIZE = 16


def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()


def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


def bytes_to_key(data, salt, output=48):
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]


def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))

password = "8810b866b8be33a1dc60af9a9c584acb".encode()

def detect_faces(img):

    img = Image.open(BytesIO(img))
    
    rects, landmarks = face_detect.detect_face(np.array(img),80);#min face size is set to 80x80
    aligns = []
    positions = []
    face_boundries = []
    for (i, rect) in enumerate(rects):
        aligned_face, face_pos = aligner.align(160,np.array(img),landmarks[:,i])
        if len(aligned_face) == 160 and len(aligned_face[0]) == 160:
            aligns.append(aligned_face)
            positions.append(face_pos)
        else: 
            print("Align face failed") #log        
    if(len(aligns) > 0):
        features_arr = extract_feature.get_features(aligns)
        no_of_faces = len(aligns)
        face_boundries = []
        for (i,rect) in enumerate(rects):
            rect = rect.tolist()
            face_boundries.append([rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]])

    else:
        no_of_faces = 0
    

    print (no_of_faces)
    
    return no_of_faces
    
@app.route("/")
def main():
    return render_template("index.html")


@app.route("/prediction", methods=["POST"])
def prediction():
    """
    curl -X POST -v -H "Content-Type: image/png" --data-binary @abba.png http://127.0.0.1:9099/prediction -o foo.jpg
    """
    if request.method == "POST":
        #image = request.data
        imagedata = request.data
        pt = decrypt(imagedata, password)
        image = base64.b64decode(pt)
        face_boundries = detect_faces(image)
        print(jsonify({ "faces": face_boundries }))
        return make_response(
                jsonify(
                    {"faces": face_boundries}
                ),
                200,
            )


if __name__ == "__main__":
    FRGraph = FaceRecGraph()
    MTCNNGraph = FaceRecGraph()
    aligner = AlignCustom()
    extract_feature = FaceFeature(FRGraph)
    face_detect = MTCNNDetect(MTCNNGraph, scale_factor=2); #scale_factor, rescales image for faster detection
    app.run(host="127.0.0.1", port=8000,ssl_context='adhoc')
