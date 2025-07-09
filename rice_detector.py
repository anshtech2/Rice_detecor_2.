
import cv2
import numpy as np
from flask import Flask, request, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            processed_path = process_image(filepath)
            return send_file(processed_path, mimetype='image/jpeg')

    return '''
    <!doctype html>
    <title>Upload Rice Image</title>
    <h1>Upload Image of Rice Grains</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=image>
      <input type=submit value=Upload>
    </form>
    '''

def process_image(image_path):
    image = cv2.imread(image_path)
    output = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50:
            continue
        x, y, w, h = cv2.boundingRect(cnt)

        # Define a broken grain as less than 30px height (adjust as needed)
        if h < 30:
            color = (0, 0, 255)  # Red for broken
        else:
            color = (0, 255, 0)  # Green for whole

        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)

    output_path = image_path.replace('.jpg', '_output.jpg')
    cv2.imwrite(output_path, output)
    return output_path

if __name__ == '__main__':
    app.run(debug=True)
