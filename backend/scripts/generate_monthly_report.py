#!/usr/bin/env python3
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.services.report_service import generate_monthly_report_excel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--property-id", type=str, default=None)
    args = parser.parse_args()

    db = SessionLocal()
    path = generate_monthly_report_excel(db, args.year, args.month, args.property_id)
    db.close()
    print(f"Report generated: {path}")


if __name__ == "__main__":
    main()
