#!/usr/bin/env python

import fitz  # PyMuPDF
from PIL import Image
import base64
import io
import os
from google.cloud import vision
import google.auth


def convert_pdf_to_images(pdf_path, dpi=300):
    """Converts each page of the PDF to an image."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images


def encode_image(image):
    """Encodes a PIL image to a base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def send_image_to_google_vision(base64_image, vision_client):
    """Sends the base64 image to Google Vision API for analysis."""
    image = vision.Image(content=base64.b64decode(base64_image))
    response = vision_client.document_text_detection(image=image)
    return response.full_text_annotation


def extract_text_annotations(text_annotation):
    """Extracts text annotations from the Vision API response."""
    extracted_text = []
    for page in text_annotation.pages:
        for block in page.blocks:
            block_text = "".join(
                [
                    symbol.text
                    for paragraph in block.paragraphs
                    for word in paragraph.words
                    for symbol in word.symbols
                ]
            )
            extracted_text.append(block_text)
    return extracted_text


def find_key_value_pairs(text_annotation, key_words=None):
    """Finds key-value pairs in the text annotation."""
    key_value_pairs = []

    for page in text_annotation.pages:
        for block in page.blocks:
            block_text = "".join(
                [
                    symbol.text
                    for paragraph in block.paragraphs
                    for word in paragraph.words
                    for symbol in word.symbols
                ]
            )
            for key_word in key_words:
                if key_word in block_text:
                    key_bbox = None
                    value_bbox = None
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = "".join(
                                [symbol.text for symbol in word.symbols]
                            )
                            if word_text == key_word:
                                key_bbox = word.bounding_box
                            elif key_bbox:
                                value_bbox = word.bounding_box
                                break
                        if key_bbox and value_bbox:
                            key_value_pairs.append((key_word, value_bbox))
                            key_bbox = None
                            value_bbox = None
    return key_value_pairs


def extract_handwritten_responses(image, key_value_pairs, vision_client):
    """Extracts handwritten responses based on key-value pairs."""
    responses = []
    for key, value_bbox in key_value_pairs:
        vertices = [(vertex.x, vertex.y) for vertex in value_bbox.vertices]
        min_x = min(vertices, key=lambda v: v[0])[0]
        min_y = min(vertices, key=lambda v: v[1])[1]
        max_x = max(vertices, key=lambda v: v[0])[0]
        max_y = max(vertices, key=lambda v: v[1])[1]

        cropped_image = image.crop((min_x, min_y, max_x, max_y))
        base64_cropped_image = encode_image(cropped_image)
        text_annotation = send_image_to_google_vision(
            base64_cropped_image, vision_client
        )
        responses.append((key, text_annotation.text if text_annotation else ""))
    return responses


def check_credentials():
    credentials, project = google.auth.default()
    if not credentials:
        print(
            "No credentials found. Please run 'gcloud auth application-default login'."
        )
        exit(1)

    # Make a low-cost API call to verify the credentials
    try:
        vision_client = vision.ImageAnnotatorClient(credentials=credentials)
        # Making a low-cost API call to list locations
        vision_client.batch_annotate_images(requests=[])
    except Exception as e:
        print(
            "Invalid or expired credentials. Please run 'gcloud auth application-default login'."
        )
        print(f"Error: {e}")
        exit(1)

    return vision_client


def main():
    pdf_path = os.getenv("FILE_PATH")
    key_words_string = os.getenv("KEY_WORDS", "")
    key_words = [kw.strip() for kw in key_words_string.split(",") if kw.strip()]

    if not pdf_path:
        print("Environment variable 'FILE_PATH' not set.")
        return

    # Initialize the Vision API client using Application Default Credentials
    vision_client = check_credentials()

    images = convert_pdf_to_images(pdf_path)
    for i, image in enumerate(images):
        print(f"Analyzing page {i + 1}...")
        base64_image = encode_image(image)
        text_annotation = send_image_to_google_vision(base64_image, vision_client)

        if text_annotation:
            extracted_text = extract_text_annotations(text_annotation)
            key_value_pairs = find_key_value_pairs(text_annotation, key_words)
            handwritten_responses = extract_handwritten_responses(
                image, key_value_pairs, vision_client
            )

            print(f"Extracted Text on page {i + 1}:")
            print("\n".join(extracted_text))

            print(f"Key-Value Pairs on page {i + 1}:")
            for key, bbox in key_value_pairs:
                print(f"{key}: {bbox}")

            print(f"Handwritten Responses on page {i + 1}:")
            for key, response in handwritten_responses:
                print(f"{key}: {response}")
        else:
            print(f"No text detected on page {i + 1}.")


if __name__ == "__main__":
    main()
