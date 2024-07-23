#!/usr/bin/env python

import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import time


def send_pdf_to_textract(s3_bucket, pdf_name):
    """Sends the PDF to AWS Textract for analysis."""
    textract = boto3.client("textract")

    response = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": s3_bucket, "Name": pdf_name}},
        FeatureTypes=["FORMS", "TABLES"],
    )

    job_id = response["JobId"]

    # Polling for the job completion
    while True:
        response = textract.get_document_analysis(JobId=job_id)
        status = response["JobStatus"]
        if status in ["SUCCEEDED", "FAILED"]:
            break
        time.sleep(5)

    if status == "SUCCEEDED":
        return response
    else:
        raise Exception(f"Textract job failed with status: {status}")


def extract_data_from_result(response):
    """Extracts text, key-value pairs, and tables from the Textract results."""
    extracted_text = []
    key_value_pairs = []
    tables = []

    try:
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                if "Text" in block:
                    extracted_text.append(block["Text"])
                else:
                    print(f"Missing 'Text' key in LINE block: {block}")
            elif (
                block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block["EntityTypes"]
            ):
                key = block.get("Text", "Key not found")
                value = None
                if "Relationships" in block:
                    for relation in block["Relationships"]:
                        if relation["Type"] == "VALUE":
                            for value_id in relation["Ids"]:
                                value_block = next(
                                    (
                                        b
                                        for b in response["Blocks"]
                                        if b["Id"] == value_id
                                    ),
                                    None,
                                )
                                if value_block and "Text" in value_block:
                                    value = value_block["Text"]
                key_value_pairs.append((key, value))
            elif block["BlockType"] == "TABLE":
                table = []
                if "Relationships" in block:
                    for relationship in block["Relationships"]:
                        if relationship["Type"] == "CHILD":
                            for cell_id in relationship["Ids"]:
                                cell_block = next(
                                    (
                                        b
                                        for b in response["Blocks"]
                                        if b["Id"] == cell_id
                                    ),
                                    None,
                                )
                                if cell_block and cell_block["BlockType"] == "CELL":
                                    text = cell_block.get("Text", "")
                                    table.append(
                                        (
                                            cell_block["RowIndex"],
                                            cell_block["ColumnIndex"],
                                            text,
                                        )
                                    )
                tables.append(table)
    except KeyError as e:
        print(f"KeyError: {e} in block {block}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return extracted_text, key_value_pairs, tables


def main():
    s3_uri = os.getenv("s3_uri")

    if not s3_uri:
        print("Environment variable 'S3_URI' not set.")
        return

    # Parse S3 URI
    if s3_uri.startswith("s3://"):
        s3_uri = s3_uri[5:]
    else:
        print("Invalid S3 URI. It should start with 's3://'.")
        return

    try:
        bucket_name, pdf_name = s3_uri.split("/", 1)

        response = send_pdf_to_textract(bucket_name, pdf_name)
        extracted_text, key_value_pairs, tables = extract_data_from_result(response)

        print(f"Extracted Text:")
        print("\n".join(extracted_text))

        print(f"Key-Value Pairs:")
        for key, value in key_value_pairs:
            if key != "Key not found" and value is not None:
                print(f"{key}: {value}")

        print(f"Tables:")
        for table in tables:
            for row, col, content in table:
                if content != "":
                    print(f"Row {row}, Column {col}: {content}")

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found. Ensure they are set in your environment.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
