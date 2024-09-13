import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from e2e_test_agent.e2e_test_agent import E2eTestingAgent
from utils.db import delete_test_logs, update_test_case_status
from utils.log_handler import SQLiteHandler
import subprocess

tests = {
    "0": "test_success_upload",
    "1": "test_unsuccessful_youtube_upload",
    "2": "test_unsuccessful_large_file_upload",
}


def test_process(queue, test_id):
    queue_handler = QueueHandler(queue)
    sqlite_handler = SQLiteHandler(test_id)
    listener = QueueListener(queue, sqlite_handler)

    try:
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)
        logger.addHandler(queue_handler)
        listener.start()

        pytest_args = [
            "pytest",
            "-s",
            "--disable-warnings",
            f"--junitxml=tmp/{tests[str(test_id)]}.xml",
            f"tests/{tests[str(test_id)]}.py",
        ]

        update_test_case_status(test_id, "in-progress")

        process = subprocess.Popen(
            pytest_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in process.stdout:
            logger.info(line.strip())
        for line in process.stderr:
            logger.error(line.strip())

        process.wait()

        import xml.etree.ElementTree as ET

        tree = ET.parse(f"tmp/{tests[str(test_id)]}.xml")
        root = tree.getroot()

        for testcase in root.iter("testcase"):
            status = "success"
            for _ in testcase.iter("failure"):
                status = "failed"
                break
            update_test_case_status(test_id, status)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        try:
            listener.stop()
            logger.removeHandler(queue_handler)
        except Exception as e:
            print(f"Failed to remove handler: {e}")


def run_test(test_id):
    delete_test_logs(test_id)

    queue = multiprocessing.Queue(-1)
    process = multiprocessing.Process(target=test_process, args=(queue, test_id))
    process.start()
    process.join()


async def run_test_with_agent(test_case):
    topic = test_case["description"]

    e2e_test_agent = E2eTestingAgent()
    await e2e_test_agent.ainvoke(topic)
