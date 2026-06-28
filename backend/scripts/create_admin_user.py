import argparse
import sys
from pathlib import Path

# Permite ejecutar el script desde backend/
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.services.user_service import create_user, get_user_by_email


def main():
    parser = argparse.ArgumentParser(
        description="Create initial KubeAudit admin user"
    )

    parser.add_argument("--full-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)

    args = parser.parse_args()

    db = SessionLocal()

    try:
        existing_user = get_user_by_email(db, args.email)

        if existing_user:
            print(f"User already exists: {args.email}")
            return

        user = create_user(
            db=db,
            full_name=args.full_name,
            email=args.email,
            password=args.password,
            role="ADMIN",
        )

        print(f"Admin user created successfully: id={user.id}, email={user.email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
