# Google PDF Tool

## Overview

This tool uses Google's Vision API to extract text from PDF files. Each page of the PDF is processed individually and the extracted text is then consumed by the LLM.

## Usage

1. Use gcloud command to do `gcloud auth application-default login` to authenticate your Google Cloud account.
1. Run the tool with the PDF file you want to process.
1. The tool will output the extracted text for each page of the PDF.

```sh
gcloud auth application-default login

gptscript eval --tools github.com/gptscript-ai/pdf-tool/google "use /path/to/pdf/file.pdf and report the contents of the file"
```

## Detailed Description

### tool.gpt

- **Name**: google_pdf_vision_ocr
- **Description**: Convert PDF to images and use Google Vision OCR to parse out text info.
- **Params**:
  - `file_path`: Path to the PDF file to analyze.
  - `max_tokens`: The number of tokens to have created by the LLM. Default 300.
  - `key_words`: Comma-separated list of key words that you want extracted as key-value pairs.

### tool.py

The `tool.py` script performs the following steps:

1. **Convert PDF to Images**: Each page of the PDF is converted to an image using the `fitz` library (PyMuPDF).
2. **Encode Image**: The image is encoded to a base64 string.
3. **Send Image to Google Vision**: The base64 image is sent to Google Vision API for analysis.
4. **Extract Text Annotations**: The text annotations are extracted from the Vision API response.
5. **Find Key-Value Pairs**: Key-value pairs are found in the text annotation based on the provided key words.
6. **Extract Handwritten Responses**: Handwritten responses are extracted based on key-value pairs.
7. **Output Extracted Data**: The extracted text, key-value pairs, and handwritten responses are printed to the console.
