"""Send request files to the local kit server and print what to check.

Adapted from the kit README step 7 `submit.py` (MIT). Each request gets a fresh request_id.

    python harness/server_submit.py <request.json> [<request.json> ...]

Exit code 1 if any case is rejected, fails, or has output issues.
"""

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
TIMEOUT = 120  # the server may count the pages of large PDFs for up to 60 s


def call(method, path, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(BASE + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.headers, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, error.headers, json.loads(error.read())


def submit(path):
    with open(path, encoding="utf-8") as handle:
        body = json.load(handle)
    body["request_id"] = f"dev-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 1000000}"
    status, headers, job = call("POST", "/v1/assessments", body)
    if status != 202:
        error = job.get("error", {})
        print(path, "rejected", status, error.get("code"), json.dumps(error.get("field_errors", [])))
        return False
    while job["job_status"] != "finished":
        time.sleep(0.5)
        _, _, job = call("GET", headers["Location"])
    result, diagnostics = job["result"], job["diagnostics"]
    issues = diagnostics.get("output_issues", [])
    print(f"{body['case']['case_id']:<14} origin={job['result_origin']:<10} "
          f"status={result['assessment_status']:<10} trl={result['predicted_trl']} "
          f"error={result['error_code']} total_ms={diagnostics.get('timings_ms', {}).get('total')}")
    if "failure" in diagnostics:
        print("   failure:", diagnostics["failure"]["message"])
    for issue in issues:
        print("   output issue:", issue["path"], issue["rule"])
    return job["result_origin"] == "module" and result["assessment_status"] != "failed" and not issues


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        sys.exit(__doc__)
    ok = all([submit(p) for p in paths])
    sys.exit(0 if ok else 1)
