# Azure PDF Tool

## Overview

This tool uses Azure's Computer Vision service to extract text from PDF files. Each page of the PDF is processed individually and the extracted text is then consumed by the LLM.

## Usage

1. You will need an Azure computer vision endpoint url and one of the keys to use this tool.
1. Run the tool with the PDF file you want to process.
1. The tool will output the extracted text for each page of the PDF.

## Example

```sh
gptscript eval --tools "github.com/gptscript-ai/pdf-tool/azure" "use /path/to/pdf/file.pdf and report the contents of the file"
```

## Detailed Description

### tool.gpt

- **Name**: azure_computer_vision_ocr
- **Description**: Uses Azure Computer Vision to extract text information from PDFs.
- **Credentials**:
  - `azureVisionKey`: Please enter Azure Vision key.
  - `azureVisionEndpoint`: Please enter Azure Vision Endpoint.
- **Params**:
  - `file_path`: Path to the PDF file on disk.

### tool.py

The `tool.py` script performs the following steps:

1. **Convert PDF to Images**: Each page of the PDF is converted to an image using the `fitz` library (PyMuPDF).
2. **Encode Image**: The image is encoded to a byte array.
3. **Send Image to Azure**: The encoded image is sent to Azure Computer Vision for analysis.
4. **Extract Data from Result**: The text is extracted from the analysis results.
5. **Output Extracted Text**: The extracted text for each page is printed to the console.
