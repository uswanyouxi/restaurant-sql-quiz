
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).resolve().parent / ".env")


def get_supabase_client():
    """Create a Supabase client for authentication."""
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )



def sign_up(email, password):
    """Register a new user with safe error reporting."""
    client = get_supabase_client()

    try:
        return client.auth.sign_up({
            "email": email,
            "password": password,
        })

    except Exception as error:
        error_type = type(error).__name__
        status = getattr(error, "status", "N/A")
        code = getattr(error, "code", "N/A")

        print("=== SIGN UP ERROR ===")
        print("Error type:", error_type)
        print("HTTP status:", status)
        print("Error code:", code)

        raise


def sign_in(email, password):
    """Sign in using email and password."""
    client = get_supabase_client()

    return client.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })


def validate_session(access_token, refresh_token):
    """Refresh a session and verify the current user."""
    client = get_supabase_client()

    session_response = client.auth.set_session(
        access_token,
        refresh_token,
    )

    if not session_response.session:
        raise ValueError("Invalid session")

    user_response = client.auth.get_user(
        session_response.session.access_token
    )

    if not user_response.user:
        raise ValueError("User verification failed")

    return session_response.session, user_response.user


def sign_out(access_token, refresh_token):
    """End the authenticated Supabase session."""
    client = get_supabase_client()

    client.auth.set_session(
        access_token,
        refresh_token,
    )

    client.auth.sign_out()
