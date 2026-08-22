import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

LANGFLOW_URL = os.getenv("LANGFLOW_URL", "http://localhost:7860")
FLOW_ID = os.getenv("FLOW_ID", "").strip()
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "").strip()

LOG_DIRECTORY = Path(__file__).resolve().parent.parent / "logs"
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
RESULT_FILE = LOG_DIRECTORY / "phase8_test_results.jsonl"

TEST_CASES = [
    {
        "id": "P8-01",
        "category": "rag_success",
        "query": "What is your return policy?",
    },
    {
        "id": "P8-02",
        "category": "operational_success",
        "query": "What is the status of ORD1002?",
    },
    {
        "id": "P8-03",
        "category": "missing_order_id",
        "query": "Where is my order?",
    },
    {
        "id": "P8-04",
        "category": "invalid_order_id",
        "query": "Check order ORD999.",
    },
    {
        "id": "P8-05",
        "category": "unknown_policy",
        "query": "What is your cryptocurrency refund policy?",
    },
    {
        "id": "P8-06",
        "category": "security_escalation",
        "query": "Someone hacked my account.",
    },
]


def run_test(test_case: dict) -> dict:
    url = f"{LANGFLOW_URL}/api/v1/run/{FLOW_ID}"

    headers = {
        "Content-Type": "application/json",
    }

    if LANGFLOW_API_KEY:
        headers["x-api-key"] = LANGFLOW_API_KEY

    payload = {
        "input_value": test_case["query"],
        "input_type": "chat",
        "output_type": "chat",
        "session_id": f"phase8-{test_case['id'].lower()}",
    }

    started = time.perf_counter()

    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": test_case["id"],
        "category": test_case["category"],
        "query": test_case["query"],
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        result["latency_ms"] = round(
            (time.perf_counter() - started) * 1000,
            2,
        )
        result["http_status"] = response.status_code
        result["success"] = response.ok

        try:
            result["response"] = response.json()
        except ValueError:
            result["response"] = response.text[:2000]

        if not response.ok:
            result["error"] = (
                f"Langflow returned HTTP {response.status_code}"
            )

    except requests.Timeout:
        result["latency_ms"] = round(
            (time.perf_counter() - started) * 1000,
            2,
        )
        result["http_status"] = None
        result["success"] = False
        result["error"] = "Request exceeded the 60-second timeout."

    except requests.ConnectionError:
        result["latency_ms"] = round(
            (time.perf_counter() - started) * 1000,
            2,
        )
        result["http_status"] = None
        result["success"] = False
        result["error"] = "Langflow service is unavailable."

    except requests.RequestException as exc:
        result["latency_ms"] = round(
            (time.perf_counter() - started) * 1000,
            2,
        )
        result["http_status"] = None
        result["success"] = False
        result["error"] = type(exc).__name__

    return result


def main() -> None:
    if not FLOW_ID:
        raise SystemExit(
            "FLOW_ID is missing. Add it to deployment/.env."
        )

    with RESULT_FILE.open("a", encoding="utf-8") as log_file:
        for test_case in TEST_CASES:
            result = run_test(test_case)
            log_file.write(json.dumps(result, ensure_ascii=False) + "\n")

            status = "PASS" if result["success"] else "ERROR"
            print(
                f"{result['test_id']} | {status} | "
                f"{result['latency_ms']} ms | "
                f"HTTP {result['http_status']}"
            )

    print(f"\nDetailed results written to: {RESULT_FILE}")


if __name__ == "__main__":
    main()