
import os
import getpass
import psycopg
from psycopg import sql
from dotenv import load_dotenv

load_dotenv()

password = getpass.getpass(
    "Enter NEW quiz_runner password: "
)

if len(password) < 16:
    raise ValueError("Password must be at least 16 characters.")

with psycopg.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    sslmode="require",
) as conn:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                sql.Identifier("quiz_runner"),
                sql.Literal(password),
            )
        )

print("quiz_runner password configured successfully.")
