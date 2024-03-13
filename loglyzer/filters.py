from typing import NamedTuple

from natsort import natsorted


class Filter(NamedTuple):
    key: str
    values: frozenset[str]

    def matches(self, o: NamedTuple) -> bool:
        return str(o._asdict()[self.key]) in self.values

    def urlencode(self) -> str:
        return "&".join(f"{self.key}={value}" for value in self.values)

    def __str__(self) -> str:
        if len(self.values) == 1:
            return f"{self.key} = {next(iter(self.values))}"
        return f"{self.key} ∈ {{{', '.join(natsorted(self.values))}}}"
