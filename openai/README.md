# OpenAI PDF Tool

## Overview

This tool uses OpenAI's GPT-4o to process and extract text from PDF files. Each page of the PDF is processed individually and the extracted text is then consumed by the LLM.

## Usage

1. Configure your OpenAI API key as an environment variable.
1. Run the tool with the PDF file you want to process.
1. The tool will output the extracted text for each page of the PDF.

## Example

```sh
export OPENAI_API_KEY="your_openai_api_key"
gptscript eval --tools github.com/gptscript-ai/pdf-tool/openai "use /path/to/pdf/file.pdf and report the contents of the file"
```

## Detailed Description

### tool.gpt

- **Name**: pdf_vision
- **Description**: Convert PDF to images and use GPT-4o vision to parse out text info.
- **Params**:
  - `file_path`: Path to the PDF file to analyze.
  - `prompt`: Information to extract from the PDF.
  - `max_tokens`: Integer value of tokens to have created by the LLM. Default is 300.

### tool.py

The `tool.py` script performs the following steps:

1. **Convert PDF to Images**: Each page of the PDF is converted to an image using the `fitz` library (PyMuPDF).
2. **Encode Image**: The image is encoded to a base64 string.
3. **Send Image to OpenAI**: The base64 image is sent to OpenAI for analysis.
4. **Output Extracted Data**: The extracted text is printed to the console.
