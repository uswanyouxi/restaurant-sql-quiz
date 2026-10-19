
from auth import get_supabase_client, validate_session


def save_answer(
    access_token: str,
    refresh_token: str,
    question_id: int,
    submitted_sql: str,
):
    """Save an answer using the authenticated user's identity."""

    if not submitted_sql or not submitted_sql.strip():
        raise ValueError("Cannot save an empty SQL answer.")

    # Verify the user's active Supabase Auth session.
    session, user = validate_session(
        access_token,
        refresh_token,
    )

    if session is None or user is None:
        raise ValueError("Authentication required.")

    # Create a fresh client for this operation.
    client = get_supabase_client()

    # Attach the verified user's session to the client.
    client.auth.set_session(
        session.access_token,
        session.refresh_token,
    )

    # RLS checks that user_id matches auth.uid().
    response = (
        client.table("quiz_submissions")
        .insert(
            {
                "user_id": str(user.id),
                "question_id": int(question_id),
                "submitted_sql": submitted_sql.strip(),
            }
        )
        .execute()
    )

    return response.data
