import os
import subprocess
from urllib.parse import urlencode

import fsspec
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from . import abuseipdb, env
from .log import Log
from .logfile import Logfile
from .templates import Templates

_templates = Templates()
_filesystem, _path = fsspec.core.url_to_fs(env.PATH)


async def _index(request: Request):
    return _templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "files": Logfile.list_dir(_filesystem, _path),
        },
    )


async def _view(request: Request):
    logfile = Logfile.parse(
        _filesystem, os.path.join(_path, request.path_params["filename"])
    )
    filters = Log.get_filters(request)
    logs = logfile.get_logs(filters)

    if "export" in request.query_params.keys():
        return PlainTextResponse("\n".join(log.export() for log in logs))

    if "report" in request.query_params.keys():
        return PlainTextResponse(abuseipdb.report(logs))

    return _templates.TemplateResponse(
        "view.html",
        {
            "request": request,
            "file": logfile,
            "filters": filters,
            "logs": logs,
            "query_wo": lambda x: urlencode(
                [
                    (key, value)
                    for key, value in request.query_params.multi_items()
                    if key != x
                ]
            ),
        },
    )


async def _whois(request: Request):
    logfile = Logfile.parse(
        _filesystem, os.path.join(_path, request.path_params["filename"])
    )
    log = list(logfile.get_logs(set()))[int(request.path_params["lineno"])]
    whois = subprocess.check_output(["whois", log.ip], encoding="utf-8")
    return _templates.TemplateResponse(
        "whois.html",
        {
            "request": request,
            "ip": log.ip,
            "whois": whois,
        },
    )


app = Starlette(
    debug=True,
    routes=[
        Route("/", _index),
        Route("/{filename}", _view),
        Route("/{filename}/{lineno}/whois", _whois),
    ],
)
