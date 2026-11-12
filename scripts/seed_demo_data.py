"""Explicit insert-only synthetic bootstrap. Never loads .env or migrates a database."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.demo_seed import seed  # noqa: E402
from app.services.errors import Phase4Error  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-synthetic", action="store_true")
    parser.add_argument("--confirm-database", required=True)
    parser.add_argument("--target-authorization", required=True)
    args = parser.parse_args()
    try:
        result = asyncio.run(
            seed(
                os.environ.get("DEMO_DATABASE_URL", ""),
                os.environ.get("APP_ENV", ""),
                args.allow_synthetic,
                args.confirm_database,
                args.target_authorization,
                os.environ.get("DATABASE_URL"),
            )
        )
        print(json.dumps(result))
        return 0
    except Phase4Error as exc:
        print(json.dumps({"error": exc.code}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
