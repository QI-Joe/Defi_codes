import hexbytes
from web3 import Web3
import pre_read 
import time
import timeit

class checker:
    w3 = None
    tx_hash=None
    event = None
    functions = None
    ABI_file = None
    file_name = None
    
    def __init__(self, path, w3, tx_hash) -> None:
        if w3 is None: 
            print("connection fails, please check it. program will stop in 3 seconds")
            time.sleep(3)
            exit(ValueError)
        self.w3=w3
            
        while tx_hash is None:
            print("Havent received any valid transaction hash, please input again")
            tx_hash = input("tx_hash: ")
        self.tx_hash=tx_hash
        
        self.event, self.functions, self.ABI_file, self.file_name = pre_read.reader(path).pre_map()
        self.file_name = Web3.toChecksumAddress(self.file_name)
    
    def get_tx(self):
        tx = self.w3.eth.get_transaction(self.tx_hash)  # this step cost the longest time
        receipt = self.w3.eth.get_transaction_receipt(self.tx_hash)
        return tx, receipt
    
    def decode_tx_info(self):
        contract = self.w3.eth.contract(address = self.file_name, abi = self.ABI_file)  # according to its source code, this actually run in local
        input, receipt = self.get_tx()
        matched = None
        
        if input['input'][0:67] in self.event:
            matched = self.event[input[0:67]]
            # special process of event, wont go into next stage  this place will be implented in next file
            # do something to variable receipt
            return matched  # do input must be function type ?
        elif input['input'][0:10] in self.functions:
            matched = self.functions[input['input'][0:10]]
            
        if matched == None: 
            print("input cannot match with current ABI files")
            return False
        
        for data in input:
            if data == 'input':
                input_result = contract.decode_function_input(input[data])
                for i in range(len(input_result[1])):
                    matched['inputs'][i]["output"] = input_result[1][matched['inputs'][i]['name']]
                matched['function full name'] = input_result[0]
            else: 
                if type(input[data]) == hexbytes.main.HexBytes:
                    matched[data] = input[data].hex()
                else: matched[data] = input[data]
        # print(matched)
        return matched
    
    
# for the rest of codes you can change them or test it by youself
def test():    
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Your Project"))
    path = input("input your json file path here: ")   #or you can skip this step and directly set your path
    start = timeit.default_timer()
    
    jack = checker(path, w3, "0x854ee8eef97da539b67cd7c9dd09c408688aa1de26d38f4dc25aaa7d052c8cc6")
    # 0x854ee8eef97da539b67cd7c9dd09c408688aa1de26d38f4dc25aaa7d052c8cc6 is a transaction hash
    
    print(jack.decode_tx_info())
    stop = timeit.default_timer()
    print("Times is: " + str(stop - start))  # this one is used to test its running time. On my computer it is about 1.2s
    
test()
