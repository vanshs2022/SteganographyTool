import numpy as np
from PIL import Image
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
KEY = os.getenv("KEY").encode()
IV = os.getenv("IV").encode()

def encrypt_text(plain_text):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)  # Create AES cipher in CBC mode
    padded_text = pad(plain_text.encode(), AES.block_size)  # Pad text
    encrypted_bytes = cipher.encrypt(padded_text)  # Encrypt text
    return base64.b64encode(encrypted_bytes).decode()  # Encode to Base64 for easy storage

def decrypt_text(encrypted_text):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)  # Create AES cipher
    encrypted_bytes = base64.b64decode(encrypted_text)  # Decode from Base64
    decrypted_text = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)  # Decrypt and remove padding
    return decrypted_text.decode()  # Convert bytes to string

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