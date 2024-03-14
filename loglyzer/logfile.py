import os
import os.path
import re
from datetime import datetime
from typing import Generator, NamedTuple

import fsspec

from . import env
from .filters import Filter
from .log import Log

_FILENAME_REGEX = re.compile(env.FILENAME_REGEX)


class InvalidLogfilenameError(ValueError):
    pass


class Logfile(NamedTuple):
    filesystem: fsspec.AbstractFileSystem
    name: str
    size: int
    date: datetime

    @classmethod
    def list_dir(
        cls, filesystem: fsspec.AbstractFileSystem, path: str
    ) -> Generator["Logfile", None, None]:
        for filename in filesystem.ls(path):
            try:
                yield cls.parse(filesystem, filename)
            except InvalidLogfilenameError:
                pass

    @classmethod
    def parse(cls, filesystem: fsspec.AbstractFileSystem, filename: str) -> "Logfile":
        if not _FILENAME_REGEX.match(os.path.basename(filename)):
            raise InvalidLogfilenameError(f"{filename} is not a valid log filename")

        file = filesystem.info(filename)

        if not file["type"] == "file":
            raise InvalidLogfilenameError(f"{filename} is not a file")

        return cls(filesystem, filename, file["size"], file["mtime"])

    def get_logs(self, filters: set[Filter]) -> Generator[Log, None, None]:
        with self.filesystem.open(self.name, "r", compression="infer") as f:
            for lineno, line in enumerate(f.readlines()):
                if (log := Log.parse(lineno, line)).matches(filters):
                    yield log
