
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from auth import get_supabase_client


def main():
    print("=== Supabase Auth Diagnostic ===")

    try:
        client = get_supabase_client()

        # Test whether Supabase Auth API is reachable
        response = client.auth.get_session()

        print("Auth client: OK")
        print("Supabase configuration: Loaded")
        print("Local session:", "Present" if response else "None")

    except Exception as error:
        print("Diagnostic failed")
        print("Error type:", type(error).__name__)
        print("HTTP status:", getattr(error, "status", "N/A"))
        print("Error code:", getattr(error, "code", "N/A"))


if __name__ == "__main__":
    main()
