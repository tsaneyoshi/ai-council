import base64

def get_base64():
    with open("test_ocr.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        print(encoded_string)

if __name__ == "__main__":
    get_base64()
