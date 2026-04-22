#!/usr/bin/env python3
"""
Create a stable pseudonymous identifier from a local identifier and an org secret.

The org secret must be supplied via the AIQT_SALT environment variable.

Example:
    export AIQT_SALT="replace-me"
    python scripts/pseudonymous_id.py --identifier alice@example.com
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identifier", required=True, help="Local identifier such as email or employee ID")
    parser.add_argument("--length", type=int, default=16, help="Length of rendered hash prefix")
    args = parser.parse_args()

    salt = os.environ.get("AIQT_SALT")
    if not salt:
        print("AIQT_SALT is not set", file=sys.stderr)
        raise SystemExit(2)

    digest = hmac.new(
        salt.encode("utf-8"),
        args.identifier.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    print(digest[: args.length])


if __name__ == "__main__":
    main()