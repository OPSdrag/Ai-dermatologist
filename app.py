from flask import Flask, request, jsonify, render_template
import numpy as np
import tensorflow as tf
import cv2, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['MODEL_PATH'] = "static/model.keras"
app.config['UPLOAD_FOLDER'] = "static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


model = tf.keras.models.load_model(app.config['MODEL_PATH'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def runNeuralNetwork(filename):
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (256, 256))

    x_test = np.array([img])
    x_test = x_test.astype('float32')
    x_test = x_test / 255.0

    pred = model.predict(x_test)[0][0]
    print(pred)
    if pred >= 0.5:
        return "Melanoma likely"
    else:
        return "Melanoma unlikely"


@app.route('/', methods=['GET'])
def displayLandingPage():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def classifyImage():
    if request.method == 'POST':
        resText = ''
        if 'image' not in request.files:
            resText = "Error uploading image"
        else:
            file = request.files['image']
            
            if file and allowed_file(file.filename) and file.filename != '':
                filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(filename)
                resText = runNeuralNetwork(filename)
            else:
                resText = "Error uploading image"
        
        response = jsonify({'resText' : resText})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)