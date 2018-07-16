
import json

#@synchronized
class Scene3Ddata:
 #   @synchronized
    def __init__(self):
        self.data = {}
        self.exit = False

#    @synchronized
    def set(self, data):
        print(data)
        temp_data = data.split(', ')
        print(temp_data)
        for item in temp_data:
            print(item, 00000)
            temp_json = json.loads('{'+item+'}')
            self.data.update(temp_json)

  #  @synchronized
    def get(self):
        return json.dumps(self.data)



json_data = Scene3Ddata()
