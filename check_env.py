#!/usr/bin/env python3
"""Check required environment variables for FareGlitch.

Usage: python check_env.py

This script prints which required and optional API environment
variables are missing. It's useful locally or in CI before deployment.
"""
import os
import sys
from dotenv import load_dotenv

# Load .env from repository root (if present)
load_dotenv()

REQUIRED = [
    "AMADEUS_API_KEY",
    "AMADEUS_API_SECRET",
    "API_SECRET_KEY",
]

OPTIONAL_APIS = [
    "DUFFEL_API_TOKEN",
    "KIWI_API_KEY",
    "HUBSPOT_API_KEY",
    "HUBSPOT_PORTAL_ID",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER",
    "SINCH_SERVICE_PLAN_ID",
    "SINCH_API_TOKEN",
    "SINCH_PHONE_NUMBER",
    "DATABASE_URL",
    "REDIS_URL",
    "SENTRY_DSN",
]


def find_missing(keys):
    return [k for k in keys if not os.getenv(k)]


def validate_env(return_missing: bool = False):
    """Validate environment variables.

    If `return_missing` is True, returns a tuple (missing_required, missing_optional).
    Otherwise, prints status and exits with code 1 when required vars are missing.
    """
    missing_required = find_missing(REQUIRED)
    missing_optional = find_missing(OPTIONAL_APIS)

    if return_missing:
        return missing_required, missing_optional

    if missing_required:
        print("Missing REQUIRED environment variables:")
        for k in missing_required:
            print(f" - {k}")
    else:
        print("All required environment variables are set.")

    print()
    print("Optional API / integration env vars not set:")
    if missing_optional:
        for k in missing_optional:
            print(f" - {k}")
    else:
        print(" - All optional integration vars present (or intentionally unset).")

    if missing_required:
        print(
            "\nTo fix: copy `railway.env.example` to `.env` or set the vars in Railway, then restart the app."
        )
        sys.exit(1)


if __name__ == "__main__":
    validate_env()
