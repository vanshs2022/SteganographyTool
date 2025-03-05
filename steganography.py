from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

def encode_image(image_path, message, output_path):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    binary_message = ''.join(format(ord(char), '08b') for char in message) + '00000000' 

    # Checking if the size of image is enough to accomodate all the bits
    if len(binary_message) > len(pixels) * 3:
        raise ValueError("Message too large for image")

    encoded_pixels = []
    binary_index = 0

    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3):
            if binary_index < len(binary_message):
                new_pixel[i] = (new_pixel[i] & ~1) | int(binary_message[binary_index])
                binary_index += 1
        encoded_pixels.append(tuple(new_pixel))

    img.putdata(encoded_pixels)
    img.save(output_path, "PNG")

def decode_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img.load()  

    pixels = list(img.getdata())

    binary_message = ""
    for pixel in pixels:
        for i in range(3):
            binary_message += str(pixel[i] & 1)

    chars = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    
    message = ""
    for char in chars:
        if char == "00000000":
            break
        message += chr(int(char, 2))

    return message


# Why we are not using this is because here it's using array which is making the code very slower, so we have used the numpy array for that reason in the updated code which made the code slight faster