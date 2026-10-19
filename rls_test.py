
import getpass

from auth import get_supabase_client


def main():
    print("=== RLS User Isolation Test ===")

    email = input("Test user email: ").strip()
    password = getpass.getpass("Test user password: ")

    client = get_supabase_client()

    response = client.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })

    if not response.user or not response.session:
        print("FAIL: Could not sign in.")
        return

    user_id = str(response.user.id)
    print("Login successful.")

    # This query uses the signed-in user's JWT.
    result = (
        client.table("quiz_submissions")
        .select("id, user_id, question_id")
        .execute()
    )

    rows = result.data or []

    print("Visible submission count:", len(rows))

    if any(str(row["user_id"]) != user_id for row in rows):
        print("FAIL: Another user's submission is visible!")
    else:
        print("PASS: No other user's submissions are visible.")


if __name__ == "__main__":
    main()
