from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import logging

from tests import run_test
from utils.csv_report import generate_csv_report
from utils.db import fetch_test_cases, fetch_test_logs, init_db, reset_all_test_cases
from tests import tests

init_db()

app = FastAPI()
logging.basicConfig(level=logging.INFO)


@app.get("/trigger-tests/{test_id}")
async def trigger_tests(test_id: int, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_test, test_id)
        return {"message": f"Test suite with test_id {test_id} initiated"}
    except Exception as e:
        logging.error(f"Error triggering tests for test_id {test_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger tests")


@app.get("/test-cases")
async def get_test_results():
    try:
        test_cases = fetch_test_cases()
        return {"data": test_cases}
    except Exception as e:
        logging.error(f"Error fetching test cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch test cases")


@app.get("/test-logs/{test_id}")
async def get_test_logs(test_id: int):
    try:
        test_logs = fetch_test_logs(test_id)
        return {"data": test_logs}
    except Exception as e:
        logging.error(f"Error fetching test logs for test_id {test_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch test logs")


@app.get("/test-reset-all")
async def reset_all_tests():
    try:
        reset_all_test_cases()
        return {"message": "success"}
    except Exception as e:
        logging.error(f"Error resetting all test cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset test cases")


@app.get("/download-test-report/{test_id}")
async def generate_report(test_id: int):
    try:
        csv_path = generate_csv_report(test_id)
        return FileResponse(
            csv_path, media_type="text/csv", filename=f"{tests[str(test_id)]}.csv"
        )
    except Exception as e:
        logging.error(f"Error generating report for test_id {test_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")
