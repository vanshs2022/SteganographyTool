import numpy as np
from PIL import Image
import os
from Crypto.Cipher import AES
import hashlib
from Crypto.Util.Padding import pad, unpad
import base64
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("KEY").encode()
IV = os.getenv("IV").encode()

def encrypt_text(plain_text):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded_text = pad(plain_text.encode(), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted_bytes).decode()

def decrypt_text(encrypted_text):
    cipher = AES.new(KEY, AES.MODE_CBC, IV) 
    encrypted_bytes = base64.b64decode(encrypted_text)
    decrypted_text = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted_text.decode()

def encode_image(image_path, message, output_path):
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)

    encrypted_message = encrypt_text(message)
    
    binary_message = ''.join(format(ord(char), '08b') for char in encrypted_message) + '00000000'

    flat_pixels = img_array.flatten()
    
    if len(binary_message) > len(flat_pixels):
        raise ValueError("Message too large for image")

    for i in range(len(binary_message)):
        flat_pixels[i] = (flat_pixels[i] & ~1) | int(binary_message[i])

    encoded_img = flat_pixels.reshape(img_array.shape)
    Image.fromarray(encoded_img).save(output_path, "PNG")

def decode_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)

    flat_pixels = img_array.flatten()
    binary_message = []
    
    for i in range(flat_pixels.size):
        binary_message.append(str(flat_pixels[i] & 1))
        if len(binary_message) >= 8 and "".join(binary_message[-8:]) == "00000000":
            break

    chars = ["".join(binary_message[i:i+8]) for i in range(0, len(binary_message)-8, 8)]
    message = "".join(chr(int(char, 2)) for char in chars)
    
    message = decrypt_text(message)

    return message

def authentication_store(image_path, password, output_path):
    """Stores the SHA-512 hash of the password inside the image using LSB steganography."""
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)

    password_hash = hashlib.sha512(password.encode()).hexdigest()

    binary_hash = ''.join(format(ord(char), '08b') for char in password_hash) + '00000000'

    flat_pixels = img_array.flatten()

    if len(binary_hash) > len(flat_pixels):
        raise ValueError("Hash too large for image")

    for i in range(len(binary_hash)):
        flat_pixels[i] = (flat_pixels[i] & ~1) | int(binary_hash[i])

    encoded_img = flat_pixels.reshape(img_array.shape)
    Image.fromarray(encoded_img).save(output_path, "PNG")


def authentication_compare(image_path, password):
    """Extracts the stored hash from the image and compares it with the hash of the provided password."""
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)

    flat_pixels = img_array.flatten()
    binary_hash = []

    for i in range(flat_pixels.size):
        binary_hash.append(str(flat_pixels[i] & 1))
        if len(binary_hash) >= 8 and "".join(binary_hash[-8:]) == "00000000":
            break

    chars = ["".join(binary_hash[i:i+8]) for i in range(0, len(binary_hash)-8, 8)]
    extracted_hash = "".join(chr(int(char, 2)) for char in chars)

    password_hash = hashlib.sha512(password.encode()).hexdigest()

    return extracted_hash == password_hash
