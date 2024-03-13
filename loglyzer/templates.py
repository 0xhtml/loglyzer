import os.path
from datetime import datetime

from starlette.templating import Jinja2Templates


class Templates(Jinja2Templates):
    def __init__(self):
        super().__init__(directory=os.path.join(os.path.dirname(__file__), "templates"))
        self.env.filters["strftime"] = datetime.strftime
        self.env.filters["basename"] = os.path.basename
