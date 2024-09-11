import csv
import xml.etree.ElementTree as ET
import os

from tests import tests
from utils.openai_client import generate_description


def generate_csv_report(test_id: int):
    csv_path = f"tmp/{tests[str(test_id)]}.csv"
    if os.path.exists(csv_path):
        return csv_path

    tree = ET.parse(f"tmp/{tests[str(test_id)]}.xml")
    root = tree.getroot()

    results = []

    for testcase in root.iter("testcase"):
        test_name = testcase.get("name")
        status = "success"
        error_message = None
        for failure in testcase.iter("failure"):
            status = "failed"
            error_message = failure.text

            results.append(
                {
                    "name": test_name,
                    "status": status,
                    "error": error_message,
                    "description": generate_description(error_message),
                }
            )

    with open(csv_path, mode="x", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Test Case Name", "Status", "Error", "Description"])
        for result in results:
            writer.writerow(
                [
                    result["name"],
                    result["status"],
                    result.get("error", ""),
                    result["description"],
                ]
            )
    return csv_path
