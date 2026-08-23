"""Health check monitoring script for deployed Streamlit Community Cloud application."""

import argparse
import os
import sys
import time

import requests


def check_health(url: str, max_retries: int = 3, retry_delay: int = 5) -> bool:
    """Verify HTTP availability and expected responses for the deployed Streamlit application."""
    if not url:
        print("ERROR: STREAMLIT_APP_URL is not set or empty.")
        print("Please configure the repository variable STREAMLIT_APP_URL.")
        return False

    print("==================================================")
    print("   Streamlit Community Cloud Health Check")
    print("==================================================")
    print(f"Target URL: {url}")
    print(f"Max Retries: {max_retries} | Retry Interval: {retry_delay}s")
    print("--------------------------------------------------")

    for attempt in range(1, max_retries + 1):
        print(f"[Attempt {attempt}/{max_retries}] Pinging {url}...")
        try:
            headers = {"User-Agent": "OraCLI-10G-HealthMonitor/1.0"}
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                print(f"Status Code: 200 OK (Content Length: {len(response.text)} bytes)")
                print("HEALTH CHECK PASSED")
                print("==================================================")
                return True
            else:
                print(f"Non-200 Status Received: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request Exception on Attempt {attempt}: {e}")

        if attempt < max_retries:
            print(f"Sleeping {retry_delay} seconds before retry...")
            time.sleep(retry_delay)

    print("--------------------------------------------------")
    print("HEALTH CHECK FAILED: Application is unreachable or unhealthy.")
    print("NOTE: If the app has hibernated, visit the URL once in a browser to resume.")
    print("==================================================")
    return False


def main() -> None:
    """Parse arguments and trigger health check."""
    parser = argparse.ArgumentParser(description="Monitor Streamlit Application Health")
    parser.add_argument(
        "--url",
        default=os.environ.get("STREAMLIT_APP_URL", ""),
        help="URL of the deployed Streamlit application",
    )
    parser.add_argument("--retries", type=int, default=3, help="Max retry attempts")
    parser.add_argument("--delay", type=int, default=5, help="Seconds between retries")

    args = parser.parse_args()
    success = check_health(url=args.url, max_retries=args.retries, retry_delay=args.delay)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
