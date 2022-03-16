import csv
from web3 import Web3
import json as basic_json
import requests
import web3.datastructures as structure
import ntpath
import ujson as json
import os
import multiprocessing as process

# auxiliary class, used to provide some important variable type.
# include web3 connection, contract factory variable, ABI file
class W3:
    w3 : Web3
    Etherscan_key : str = "Your Etherscan developer key"
    Abi : structure.AttributeDict
    contract_factory = None 
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Your_project"))
        if not self.w3.isConnected(): raise ConnectionError("cannot establish web3 object, check your web connection")
    
    def w3_provider(self):
        return self.w3
    # if input ABI doesnt exist, program would go to etherscan to match the ABI file according to given address(contract address)
    def Abi_Get(self, Address : str, ABI : dict):
        Address = Web3.toChecksumAddress(Address)
        if ABI is None:
            connector = f"https://api.etherscan.io/api?module=contract&action=getabi&address={Address}&apikey={self.Etherscan_key}"
            self.Abi = basic_json.loads(requests.get(connector).text)
        else : 
            self.Abi = ABI
        self.contract_factory = self.w3.eth.contract(address=Address, abi= self.Abi["result"])
        
    # return a factory type variable
    def contract_factory_provider(self):
        if self.contract_factory == None:
            raise ValueError("cannot return correct factory object, please check your input address and Etherscan Key")
        return self.contract_factory
    
    # return ABI file
    def Abi_provider(self):
        if self.Abi == None:
            raise ValueError("can not get Abi")
        return self.Abi
    
provider : W3 = W3()

class Reader:
    # if any debug problem happened, pls check there first
    path : str = "/ABI_files/"
    
    def __init__(self, path : str) -> None:
        self.path += path
    
    def my_read_json(self):
        with open (self.path, 'r') as fp:                        #, default = lambda  obj:obj.__dict__, sort_keys=True, indent=4
            files = json.load(fp)
        fp.close()
        return files                                                                             

    # return type: a dictionary with four items
    # which stores event ABI, functions ABI
    # and full ABI files(above three are dict), contract address with string type
    def pre_map(self):                                                          
        file = self.my_read_json()
        if not file:
            print("this tx doesnt upload its source code.")
            return False, False, False, False
        
        event, functions = dict(), dict()
        contract_address = ntpath.basename(self.path)[:-5]
        for parenthetical in file:
            if (parenthetical['type'] == 'event'): event[parenthetical['signature']] = parenthetical
            elif (parenthetical['type'] == 'function'): functions[parenthetical["signature"]] = parenthetical
        return {"event" : event, "functions" : functions, "ABI_files" : file, "contract_address": contract_address}

# used to detect the path existence
# return bool
def contract_detect(path):
    return os.path.isfile(path)

def function_hash(item:dict):
    if ('inputs' not in item.keys()):
        return
    input_list = [input_item['type'] for input_item in item['inputs']]
    full_name = item['name'] + '(' + ','.join(input_list) + ')'
    fhash=Web3.keccak(text = full_name)
    fhash=fhash.hex()
    return fhash

def ABI_adjustor(Abi):
    if Abi['message']!='OK' or (Abi['result'] is None): 
        return False
    result = basic_json.loads(Abi['result'])
    functions, event  = [], []
    # pre divide and classfy the different ABI
    for bracket in result:
        if (bracket["type"] == "function"): 
            bracket["signature"] = function_hash(bracket)[0:10]
            functions.append(bracket)
        elif (bracket["type"] == "event"): 
            bracket["signature"] = function_hash(bracket)  #  event_hash(parenthetical["name"])
            event.append(bracket)
        else: bracket["signature"] = bracket["type"]
    return result, {"functions": functions, "event": event}

# store ABI files as json
def abi_json_writer(input_path, abi_files):
    path=input_path
    with open(path, 'w') as final_step:
        basic_json.dump(abi_files, final_step, ensure_ascii=False, indent=4)
    final_step.close()
    return

def abi_csv_writer(csv_write_path : str, file_content : list):
    target_csv = open(csv_write_path, 'a+', newline= "" )
    longest_dict = max([(file_content.index(rdict), len(rdict.values())) for rdict in file_content], key = lambda value: value[1])
    csvW = csv.DictWriter(target_csv, fieldnames = file_content[longest_dict[0]].keys())
    csvW.writeheader()
    csvW.writerows(file_content)
    target_csv.close()
    return

def combine_tx(contract_hash : str):
    path : str= "D:/pycharm/simulate/ABI_files/" + contract_hash + ".json"
    if contract_hash is None: return False
    
    # first, if we have Corresponding file
    if contract_detect(path):
        return Reader(contract_hash + '.json').pre_map()
    
    # if we dont have 
    #this statement could provide target ABI for decoding input
    provider.Abi_Get(contract_hash, None)
    # this step is used to provide ABI for event process
    abi, info = ABI_adjustor(provider.Abi_provider())
    # here, the ABI file is not been processed
    info["ABI_files"] = provider.Abi_provider()
    info["contract_address"] = Web3.toChecksumAddress(contract_hash)
    # in here since we dont have this ABI, program will branch to two part
    # one part write down ABI as json format, another part go to decode tx
    p1 = process.Process(target= abi_json_writer, args= (contract_hash + ".json", abi, ))
    # it is fine that in there without p1.join()
    p1.start()
    
    return info


