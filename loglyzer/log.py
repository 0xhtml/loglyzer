import re
from datetime import datetime
from typing import NamedTuple

from starlette.requests import Request

from . import env
from .filters import Filter

_LINE_REGEX = re.compile(env.LINE_REGEX)


class InvalidLogError(ValueError):
    pass


class Log(NamedTuple):
    lineno: int
    ip: str
    date: datetime
    method: str
    path: str
    http: str
    status: int
    size: int
    domain: str
    referer: str
    useragent: str

    @classmethod
    def parse(cls, lineno: int, line: str) -> "Log":
        match = _LINE_REGEX.match(line)

        if not match:
            raise InvalidLogError(f"Invalid log line: {line}")

        return cls(
            lineno,
            match.group("ip"),
            datetime.strptime(match.group("date"), env.DATETIME_FORMAT),
            match.group("method"),
            match.group("path"),
            match.group("http"),
            int(match.group("status")),
            int(match.group("size")) if match.group("size") != "-" else 0,
            match.group("domain"),
            match.group("referer") if match.group("referer") != "-" else "",
            match.group("useragent"),
        )

    @classmethod
    def get_filters(cls, request: Request) -> set[Filter]:
        return {
            Filter(key, frozenset(request.query_params.getlist(key)))
            for key in cls._fields
            if key in request.query_params.keys()
        }

    def matches(self, filters: set[Filter]) -> bool:
        return all(_filter.matches(self) for _filter in filters)

    def export(self) -> str:
        return (
            f"{self.ip} - [{self.date.strftime('%d/%b/%Y:%H:%M:%S %z')}] "
            f"\"{self.method} {self.path} {self.http}\" {self.status} "
            f"{self.size} {self.domain} \"{self.referer}\" \"{self.useragent}\""
        )
