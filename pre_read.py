import ujson as json

class reader:
    path = ""
    
    def __init__(self, path) -> None:
        self.path = path
        pass 
    
    def my_read_json(self):
        with open (self.path, 'r') as fp:                        #, default = lambda  obj:obj.__dict__, sort_keys=True, indent=4
            files = json.load(fp)
        print(type(files))
        fp.close()
        return files                                                                              # can we merge my_read_json and pre_map into one?
                                                                                                       # I mean, mapping signature with every parenthetical while reading the json file
    def pre_map(self) -> dict:                                                          # so this only need Theta(n) times instead of scanning whole file twice
        file = self.my_read_json()
        stores = dict()
        for parenthetical in file:
            stores[parenthetical["signature"]] = parenthetical
        return stores