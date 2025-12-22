import requests
import io
from PIL import Image, ImageDraw, ImageFont

# Define the endpoint
url = "http://localhost:8001/product/parse"

def create_dummy_image():
    # Create a white image with black text
    img = Image.new('RGB', (200, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    # Use default font
    d.text((10, 40), "TEST 1234", fill=(0, 0, 0))
    
    # Save to BytesIO object
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def create_dummy_html():
    content = """
    <html>
        <body>
            <h1>Product Name: Eco Soap</h1>
            <p>Description: This is an eco-friendly soap.</p>
            <p>GTIN: 1234567890123</p>
        </body>
    </html>
    """
    return io.BytesIO(content.encode('utf-8'))

def test_parser():
    print(f"Testing API at {url}...")
    
    # 1. Image Test
    print("\n--- Testing Image Upload (OCR) ---")
    image_file = create_dummy_image()
    files = [
        ('files', ('test_image.png', image_file, 'image/png'))
    ]
    try:
        response = requests.post(url, files=files, data={"gtin": "0000000000000"})
        if response.status_code == 200:
            print("Success!")
            print("Response:", response.json())
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print(f"Error: {e}")

    # 2. HTML Test
    print("\n--- Testing HTML Upload ---")
    html_file = create_dummy_html()
    files = [
        ('files', ('test_product.html', html_file, 'text/html'))
    ]
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            print("Success!")
            print("Response:", response.json())
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_parser()
