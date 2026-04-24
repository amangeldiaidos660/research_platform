from __future__ import annotations

from fastapi import HTTPException, status


def parse_optional_int_query(value: str | int | None, field_name: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "int_parsing",
                    "loc": ["query", field_name],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "input": value,
                }
            ],
        ) from exc
