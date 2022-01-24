import ujson as json

class reader:
    path = "D:\pycharm\simulate\ABI_files\0xc4269cc7acdedc3794b221aa4d9205f564e27f0d.json"
    
    def __init__(self) -> None:
        # self.path = path
        pass 
    
    def my_read_json(self):
        with open (self.path, 'r') as fle:
            files = json.loads(fle)
        print(type(files))
        return files                                                                              # can we merge my_read_json and pre_map into one?
                                                                                                       # I mean, mapping signature with every parenthetical while reading the json file
    def pre_map(self) -> dict:                                                          # so this only need Theta(n) times instead of scanning whole file twice
        file = self.my_read_json()
        stores = dict()
        for parenthetical in file:
            stores[parenthetical["signature"]] = parenthetical
        return stores