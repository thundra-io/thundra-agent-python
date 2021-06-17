import json


class JSONEncoder(json.JSONEncoder):
    def default(self, z):
        try:
            if isinstance(z, bytes):
                return z.decode('utf-8', errors='ignore')
            elif "to_json" in dir(z):
                return z.to_json()
            else:
                return super(JSONEncoder, self).default(z)
        except Exception as e:
            print(e)


def to_json(data, separators=None):
    return json.dumps(data, separators=separators, cls=JSONEncoder)
