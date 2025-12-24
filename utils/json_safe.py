import json
from datetime import datetime, date


def json_safe(obj):
    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return str(o)

    return json.loads(json.dumps(obj, default=default))
