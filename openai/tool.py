#!/usr/bin/env python

import fitz  # PyMuPDF
from PIL import Image
import base64
import io
import os
import requests


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
    """Encodes a PIL image to a base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def send_image_to_openai(prompt, base64_image, api_key):
    """Sends the base64 image to OpenAI for analysis."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    max_tokens = os.getenv("max_tokens", 300)

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": int(max_tokens),
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    return response.json()


def main():
    pdf_path = os.getenv("FILE_PATH")
    api_key = os.getenv("OPENAI_API_KEY")
    prompt = os.getenv("prompt", "What is in this image?")

    if not pdf_path:
        print("Environment variable 'file_path' not set.")
        return

    if not api_key:
        print("Environment variable 'OPENAI_API_KEY' not set.")
        return

    images = convert_pdf_to_images(pdf_path)
    for i, image in enumerate(images):
        # print(f"Analyzing page {i + 1}...")
        base64_image = encode_image(image)
        result = send_image_to_openai(prompt, base64_image, api_key)
        print(result)


if __name__ == "__main__":
    main()
