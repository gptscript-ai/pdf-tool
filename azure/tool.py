#!/usr/bin/env python

import fitz  # PyMuPDF
from PIL import Image
import io
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time


def convert_pdf_to_images(pdf_path):
    """Converts each page of the PDF to an image."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images


def encode_image(image):
    """Encodes a PIL image to a byte array."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def send_image_to_azure(image_data, computer_vision_client):
    """Sends the image data to Azure Computer Vision for analysis."""
    # Create a stream from the image data
    image_stream = io.BytesIO(image_data)

    # Call the API with the image stream
    read_response = computer_vision_client.read_in_stream(image_stream, raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for the retrieval of the results
    while True:
        read_result = computer_vision_client.get_read_result(operation_id)
        if read_result.status not in ["notStarted", "running"]:
            break
        time.sleep(1)

    # Return the results
    return read_result.analyze_result.read_results


def extract_data_from_result(results):
    """Extracts text from the Computer Vision results."""
    extracted_text = []
    for page in results:
        for line in page.lines:
            extracted_text.append(line.text)
    return extracted_text


def main():
    pdf_path = os.getenv("FILE_PATH")
    endpoint = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")
    key = os.getenv("AZURE_COMPUTER_VISION_KEY")

    if not pdf_path:
        print("Environment variable 'file_path' not set.")
        return

    if not endpoint or not key:
        print("Azure Computer Vision endpoint and key must be set.")
        return

    computer_vision_client = ComputerVisionClient(
        endpoint, CognitiveServicesCredentials(key)
    )

    images = convert_pdf_to_images(pdf_path)
    for i, image in enumerate(images):
        print(f"Analyzing page {i + 1}...")
        image_data = encode_image(image)
        results = send_image_to_azure(image_data, computer_vision_client)

        extracted_text = extract_data_from_result(results)

        print(f"Extracted Text on page {i + 1}:")
        print("\n".join(extracted_text))


if __name__ == "__main__":
    main()
