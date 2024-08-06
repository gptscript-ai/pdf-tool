# PDF Tools

## Overview

This repository contains a collection of lower level tools to work with PDF files using major cloud provider OCR tools. Each of the tools will extract one page at a time from the PDF file and send it to the OCR service. The extracted text will be consumed by the LLM.

## Tools

- [Azure](./azure) - Uses Computer Vision
- [Google](./google) - Uses Vision API
- [AWS](./aws) - Uses Textract
- [OpenAI GPT-4o](./openai)
