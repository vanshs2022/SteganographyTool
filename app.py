import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from steganography_updated import encode_image, decode_image, authentication_store, authentication_compare

app = Flask(__name__)

UPLOAD_FOLDER = "static/tmp"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/password")
def password_page():
    return render_template("password.html")

@app.route("/store_password", methods=["POST"])
def store_password():
    password = request.form["password"]
    image = request.files["image"]

    if image.filename == "":
        return render_template("password.html", message="No image selected for storing password!")

    filename = secure_filename(image.filename)
    img_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(img_path)
    
    hashed_filename = "hashed_" + filename
    hashed_img_path = os.path.join(app.config["UPLOAD_FOLDER"], hashed_filename)

    authentication_store(img_path, password, hashed_img_path)

    hashed_img_rel = os.path.join("tmp", hashed_filename)  

    return render_template("password.html", message="Password stored successfully!", download_image=hashed_img_rel)


@app.route("/compare_password", methods=["POST"])
def compare_password():
    password = request.form["password"]
    image = request.files["image"]

    if image.filename == "":
        return render_template("password.html", message="No image selected for verifying password!")

    img_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(image.filename))
    image.save(img_path)

    if authentication_compare(img_path, password):
        return render_template("password.html", message="Password match!")
    else:
        return render_template("password.html", message="Password does not match!")

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
