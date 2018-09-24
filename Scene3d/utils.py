import json


# @synchronized
class Scene3Ddata:
    # @synchronized
    def __init__(self, filename='data.json'):
        self._filename = filename
        with open(filename, 'r', encoding='utf-8') as infile:
            self.data = json.loads(infile.read())
        self.exit = False

    # @synchronized
    def add(self, data):
        temp_data = data.split(', ')
        for item in temp_data:
            # (item, 00000)
            try:
                json_like_str = f'{{ {item} }}'
                print('Format json:', json_like_str)
                temp_json = json.loads(json_like_str)
                self.data.update(temp_json)
                with open(self._filename, 'w', encoding='utf-8') as outfile:
                    json.dump(self.data, outfile)
                    print('Write to file')
            except Exception:
                pass

    # @synchronized
    def get(self):
        return json.dumps(self.data)


json_data = Scene3Ddata()
