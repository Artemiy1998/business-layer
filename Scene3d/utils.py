import json


# @synchronized
class Scene3Ddata:
    # @synchronized
    def __init__(self):
        self.data = {}
        self.exit = False

    # @synchronized
    def add(self, data):
        temp_data = data.split(', ')
        for item in temp_data:
            # (item, 00000)
            try:
                temp_json = json.loads(f'{item}')
                self.data.update(temp_json)
            except Exception:
                pass

    # @synchronized
    def get(self):
        return json.dumps(self.data)


json_data = Scene3Ddata()
