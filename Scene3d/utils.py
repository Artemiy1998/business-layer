
import json

#@synchronized
class Scene3Ddata:
 #   @synchronized
    def __init__(self):
        self.data = {}
        self.exit = False

#    @synchronized
    def set(self, data):
        #(data)
        temp_data = data.split(', ')
        #(temp_data)
        for item in temp_data:
            #(item, 00000)
            try:
                temp_json = json.loads('{'+item+'}')

                self.data.update(temp_json)
            except Exception:
                pass

  #  @synchronized
    def get(self):
        return json.dumps(self.data)



json_data = Scene3Ddata()
