import json
from server.core.schemas.product.product_entity import Product

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Product):
            return str(obj.model_dump())
        return json.JSONEncoder.default(self, obj)

class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.custom_hook, *args, **kwargs)

    def custom_hook(self, dct):
        result = {}
        for key, value in dct.items():
            result[int(key)] = Product(**eval(value))
        return result

class Storage:
    def __init__(self, path):
        self.path = path
        try:
            with open(path, "r") as f:
                self.data = json.load(f, cls=CustomDecoder)
        except FileNotFoundError as e:
            self.data = {}

    def get_data(self):
        return self.data

    def dump(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, cls=CustomEncoder)

storages = {}
def get_storages():
    global storages
    return storages

def get_storage(path):
    global storages
    if path not in storages:
        storages[path] = Storage(path)
    return storages[path]