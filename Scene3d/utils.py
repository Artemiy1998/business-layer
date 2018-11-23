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
            json_like_str = f'{{ {item} }}'
            print('Format json:', json_like_str)
            try:
                temp_json = json.loads(json_like_str)
                self.data.update(temp_json)
            except ValueError as e:
                print('Exception during parsing json:', e)

    # @synchronized
    def get(self):
        return json.dumps(self.data)

    def get_by_parameter(self, parameter):
        if parameter not in self.data:
            return 'None'
        return self.data[parameter]


json_data = Scene3Ddata()
