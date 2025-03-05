import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from steganography_updated import encode_image, decode_image
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/encode", methods=["POST"])
def encode():
    image = request.files["image"]
    message = request.form["message"]

    if image.filename == "":
        return "No selected file"

    img_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(image.filename))
    image.save(img_path)

    encoded_img_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_" + image.filename)
    encode_image(img_path, message, encoded_img_path)

    return render_template("result.html", image=encoded_img_path, message="Message encoded successfully!", mode="encode")   

@app.route("/decode", methods=["POST"])
def decode():
    image = request.files["image"]

    if image.filename == "":
        return "No selected file"

    img_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(image.filename))
    image.save(img_path)

    try:
        hidden_message = decode_image(img_path)
    except Exception as e:
        return render_template("result.html", message=f"Error decoding image: {e}", mode="decode")

    return render_template("result.html", message=f"{hidden_message}", mode="decode")


if __name__ == "__main__":
    app.run(debug=True)