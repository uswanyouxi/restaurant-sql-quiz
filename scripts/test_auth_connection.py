
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from auth import get_supabase_client


def main():
    try:
        client = get_supabase_client()

        if client.auth is not None:
            print("Supabase Auth client initialized successfully.")
        else:
            print("Supabase Auth client initialization failed.")

    except Exception as error:
        print("Auth initialization failed.")
        print("Error type:", type(error).__name__)


if __name__ == "__main__":
    main()

