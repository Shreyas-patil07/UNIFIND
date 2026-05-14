#!/usr/bin/env python3
"""
Health check script for UNIFIND backend.
Can be used for monitoring, load balancer health checks, or deployment verification.
"""
import argparse
import json
import sys
import time
import urllib.request
from typing import Any, Dict


def check_endpoint(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check a single endpoint.

    Args:
        url: Endpoint URL to check
        timeout: Request timeout in seconds

    Returns:
        Dict with status, response_time, and data
    """
    start_time = time.time()

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            response_time = time.time() - start_time
            data = json.loads(response.read().decode())

            return {
                "status": "healthy",
                "status_code": response.status,
                "response_time": round(response_time * 1000, 2),  # ms
                "data": data,
            }
    except urllib.error.HTTPError as e:
        response_time = time.time() - start_time
        return {
            "status": "unhealthy",
            "status_code": e.code,
            "response_time": round(response_time * 1000, 2),
            "error": str(e),
        }
    except urllib.error.URLError as e:
        response_time = time.time() - start_time
        return {
            "status": "unreachable",
            "status_code": None,
            "response_time": round(response_time * 1000, 2),
            "error": str(e),
        }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "status": "error",
            "status_code": None,
            "response_time": round(response_time * 1000, 2),
            "error": str(e),
        }


def main():
    """Run health checks."""
    parser = argparse.ArgumentParser(description="UNIFIND Backend Health Check")
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="Backend host URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print(f"🏥 UNIFIND Backend Health Check")
    print(f"{'='*60}")
    print(f"Host: {args.host}")
    print(f"Timeout: {args.timeout}s")
    print(f"{'='*60}\n")

    # Define endpoints to check
    endpoints = {
        "Root": f"{args.host}/",
        "Health": f"{args.host}/health",
        "API Health": f"{args.host}/api/health",
        "Readiness": f"{args.host}/api/ready",
    }

    results = {}
    all_healthy = True

    # Check each endpoint
    for name, url in endpoints.items():
        print(f"Checking {name}... ", end="", flush=True)
        result = check_endpoint(url, args.timeout)
        results[name] = result

        if result["status"] == "healthy":
            print(f"✅ {result['response_time']}ms")
        else:
            print(f"❌ {result['status']}")
            all_healthy = False

        if args.verbose and result.get("data"):
            print(f"  Response: {json.dumps(result['data'], indent=2)}")

        if result.get("error"):
            print(f"  Error: {result['error']}")

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")

    healthy_count = sum(1 for r in results.values() if r["status"] == "healthy")
    total_count = len(results)

    print(f"Healthy: {healthy_count}/{total_count}")

    avg_response_time = sum(r["response_time"] for r in results.values()) / total_count
    print(f"Average Response Time: {avg_response_time:.2f}ms")

    if all_healthy:
        print("\n✅ All checks passed!")
        return 0
    else:
        print("\n❌ Some checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
