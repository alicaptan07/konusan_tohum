def report(test_results):
    total = len(test_results)
    passed = sum(1 for result in test_results.values() if result)
    failed = total - passed
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "status": "OK" if failed == 0 else "WARNING"
    }

def ping():
    return "OK"