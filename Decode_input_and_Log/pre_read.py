from importlib.resources import path
import ntpath
import ujson as json

class reader:
    path = ""
    
    def __init__(self, path) -> None:
        self.path = path
    
    def my_read_json(self):
        with open (self.path, 'r') as fp:                        #, default = lambda  obj:obj.__dict__, sort_keys=True, indent=4
            files = json.load(fp)
        print(type(files))
        fp.close()
        return files                                                                              # can we merge my_read_json and pre_map into one?
                                                                                                       # I mean, mapping signature with every parenthetical while reading the json file
    def pre_map(self):                                                          # so this only need Theta(n) times instead of scanning whole file twice
        file = self.my_read_json()
        event, functions = dict(), dict()
        contract_address = ntpath.basename(self.path)[:-5]
        for parenthetical in file:
            if (parenthetical['type'] == 'event'): event[parenthetical['signature']] = parenthetical
            elif (parenthetical['type'] == 'function'): functions[parenthetical["signature"]] = parenthetical
        return event, functions, file, contract_address
