from datetime import datetime

import httpx

from . import env
from .log import Log


class AbuseIPDBError(Exception):
    pass


def _frmt_date(date: datetime) -> str:
    string = date.strftime("%Y-%m-%dT%H:%M:%S%z")
    return f"{string[:-2]}:{string[-2:]}"


def report(logs: list[Log]) -> str:
    if not all(log.ip == logs[0].ip for log in logs[1:]):
        raise AbuseIPDBError("All logs must have the same IP")

    text = "\n".join(log.export() for log in logs)[:1024] + "\n"
    text = text[: text.rfind("\n")]

    resp = httpx.post(
        "https://api.abuseipdb.com/api/v2/report",
        headers={
            "Key": env.ABUSEIPDB_KEY,
            "Accept": "application/json",
        },
        data={
            "ip": logs[0].ip,
            "categories": "21",
            "comment": text,
            "timestamp": _frmt_date(logs[0].date),
        },
    )

    return resp.content
