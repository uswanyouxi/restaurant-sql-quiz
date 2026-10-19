
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

url = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_KEY"]

print("=== Supabase Python HTTPS Test ===")

for trust_env in (True, False):
    print(f"\nTesting trust_env={trust_env}")

    try:
        with httpx.Client(
            timeout=15,
            trust_env=trust_env,
        ) as client:
            response = client.get(
                f"{url}/auth/v1/health",
                headers={"apikey": key},
            )

            print("HTTP status:", response.status_code)
            print("HTTP request completed.")


    except Exception as error:
        print("Request failed.")
        print("Error type:", type(error).__name__)

        # Show exception categories without exposing secrets.
        current = error
        level = 0

        while current is not None and level < 5:
            print(
                f"Level {level}:",
                type(current).__name__
            )

            current = current.__cause__
            level += 1

import socket

print("\n=== Python DNS Test ===")

hostname = os.environ["SUPABASE_URL"].split("//")[-1].split("/")[0]

try:
    addresses = socket.getaddrinfo(
        hostname,
        443,
        type=socket.SOCK_STREAM,
    )

    for address in addresses:
        print(
            "Address family:",
            "IPv6" if address[0] == socket.AF_INET6 else "IPv4"
        )

    print("Python DNS resolution successful.")

except Exception as error:
    print("Python DNS resolution failed.")
    print("Error type:", type(error).__name__)


from urllib.parse import urlparse

print("\n=== Supabase URL Configuration Check ===")

raw_url = os.environ["SUPABASE_URL"]
parsed = urlparse(raw_url)

expected_host = "gwhvlwcwhubvpbmbtsco.supabase.co"

print("HTTPS scheme correct:", parsed.scheme == "https")
print("Hostname matches project:", parsed.hostname == expected_host)
print("Unexpected URL path:", bool(parsed.path.strip("/")))
print("Unexpected URL whitespace:", raw_url != raw_url.strip())
print("Unexpected URL port:", parsed.port is not None)
