
import getpass
from uuid import UUID

from auth import get_supabase_client


def main():
    print("=== RLS INSERT Isolation Test ===")

    email = input("Test user B email: ").strip()
    password = getpass.getpass("Test user B password: ")

    # Enter user A's UUID, not a password or access token.
    target_user_id = input("User A UID: ").strip()

    try:
        target_user_id = str(UUID(target_user_id))
    except ValueError:
        print("FAIL: Invalid UUID format.")
        return

    client = get_supabase_client()

    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if not response.user or not response.session:
            print("FAIL: User B login failed.")
            return

        current_user_id = str(response.user.id)

        if current_user_id == target_user_id:
            print("TEST INVALID: User A and B are the same.")
            return

        print("User B login successful.")

        # Attempt to insert a submission under user A's UID.
        result = (
            client.table("quiz_submissions")
            .insert({
                "user_id": target_user_id,
                "question_id": 1,
                "submitted_sql": "SELECT 1;",
            })
            .execute()
        )

        print("FAIL: Unauthorized INSERT was accepted!")
        print("Please inspect database policies immediately.")

    except Exception as error:
        error_code = getattr(error, "code", None)
        status_code = getattr(error, "status", None)

        if error_code == "42501":
            print("PASS: RLS rejected the unauthorized INSERT.")
        else:
            print("TEST INCONCLUSIVE: Request failed.")
            print("Error type:", type(error).__name__)
            print("Error code:", error_code or "N/A")
            print("HTTP status:", status_code or "N/A")


if __name__ == "__main__":
    main()
