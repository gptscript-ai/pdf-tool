# AWS PDF Tool

## Overview

This tool uses AWS Textract to extract text from PDF files. Each page of the PDF is processed individually and the extracted text is then consumed by the LLM.

## Usage

1. Ensure you have an AWS account and have set up Textract.
2. Configure your AWS credentials in the tool's configuration file.
3. Run the tool with the PDF file you want to process.
4. The tool will output the extracted text for each page of the PDF.

## Configuration

- AWS credentials. Since there are many ways to interact with AWS, the tool relies on the environment being setup with AWS Creds that can be picked up by the AWS SDK client.

## Example

For example, this uses the simplest way to setup AWS creds on a local machine.

```sh
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
export AWS_REGION="your_aws_region"
gptscript eval --tools github.com/gptscript-ai/pdf-tool/aws "use s3://mybucket/foo.pdf and report the contents of the file"
```

## Detailed Description

### tool.gpt

- **Name**: aws_textract
- **Description**: Use AWS Textract to get content out of PDF files.
- **Params**:
  - `s3_uri`: The bucket in `s3://<bucket>/<content>` format.

### tool.py

The `tool.py` script performs the following steps:

1. **Send PDF to Textract**: The PDF is sent to AWS Textract for analysis.
2. **Extract Data from Result**: The text, key-value pairs, and tables are extracted from the analysis results.
3. **Output Extracted Data**: The extracted text, key-value pairs, and tables are printed to the console.
