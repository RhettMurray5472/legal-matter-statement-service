import argparse
import json
from pathlib import Path

from .infrai_client import InfraiClient
from .models import StatementRequest
from .statement_service import export_statement


def main() -> None:
    parser = argparse.ArgumentParser(description="Export one legal matter statement")
    parser.add_argument("request", type=Path, help="Path to a statement request JSON file")
    args = parser.parse_args()
    request = StatementRequest.model_validate_json(args.request.read_text(encoding="utf-8"))
    result = export_statement(request, InfraiClient())
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
