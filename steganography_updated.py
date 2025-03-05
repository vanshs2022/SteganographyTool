import numpy as np
from PIL import Image

def encode_image(image_path, message, output_path):
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)

    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000'

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

    return message

# Numpy use made the code faster than the arrays and the similar reason for is there for it's use in ML as arrays make the code slower, even some platforms listed that numpy is around 10x faster than the array