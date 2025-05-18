import json

from jinja2.ext import Extension

from correspondence.utils import get_countries


class CorrespondenceExtension(Extension):
    def __init__(self, environment, app=None):
        super().__init__(environment)

        environment.globals["COUNTRIES"] = get_countries()
        environment.filters["jsonify"] = json.dumps
