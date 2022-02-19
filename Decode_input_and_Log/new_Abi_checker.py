from ast import Bytes
import string
import hexbytes
from web3 import Web3
import pre_read 
import time
import timeit
import Abi_convert
from event_process import event_checker
from times import time_longth, block_tx

class checker:
    
    # declare some global variables and specify their data type
    # if in future we need to link to our own server, w3 need to be Web3.geth
    w3 : Web3.HTTPProvider 
    tx_hash : string
    event : dict
    functions : dict
    ABI_file = None
    file_name : string
    path : string = ""  # you need to reset your path, remember to add a extra "/" in the last
    
    # Otimes is used to calculate running time
    Otimes = time_longth()
    
    def __init__(self, w3, tx_hash) -> None:
        if w3 is None: 
            print("connection fails, please check it. program will stop in 3 seconds")
            time.sleep(3)
            exit(ValueError)
        self.w3=w3
            
        while tx_hash is None:
            print("Havent received any valid transaction hash, please input again")
            tx_hash = input("tx_hash: ")
        self.tx_hash=tx_hash
    
    
    # Address in there has been checked
    def file_get(self, Address : string) -> None:  
        if not pre_read.contract_detect(self.path + Address + ".json"): 
            Abi_convert.combine_tx(Address, 2)
        self.event, self.functions, self.ABI_file, self.file_name = pre_read.reader(Address + '.json').pre_map()
        if not self.event: return 
        
        # file_name in there is address of corresponding contract
        self.file_name = Web3.toChecksumAddress(self.file_name)  
    
    # if Im right to Object contract, then there is the ONLY place need to connect to outer website
    def get_tx(self):
        tx = self.w3.eth.get_transaction(self.tx_hash)  # this step cost the longest time
        receipt = self.w3.eth.get_transaction_receipt(self.tx_hash)
        return tx, receipt
    
    # the order of this function is first process input then decode logs, 
    # But the two parts don't conflict in terms of data/ABI reading, maybe we can use multithreading to speed it up?
    def decode_tx_info(self) ->list:
        # time calculator
        self.Otimes.Nstart0(timeit.default_timer())  
        input, receipt = self.get_tx()
        
        self.file_get(Web3.toChecksumAddress(input['to']))
        if not self.event: return False,  False
        
        contract = self.w3.eth.contract(address = self.file_name, abi = self.ABI_file)  # according to its source code, actually, this step run in local
        matched = None
        
        # somehow for some tx's input signature is not stored in its contract, or even some tx do not provide decodable ABI
        # so, actually for input abi we should get it from a database
        
        matched = self.functions[input['input'][0:10]]
        # global matched
        # matched += self.functions[input['input'][0:10]]
        
        if matched == None: 
            print("input cannot match with current ABI files")
            return 0, False
        
        # briefly, this step only write data get from blockchain(?)/Etherscan into specified dict object
        for data in input:
            if data == 'input':
                input_result = contract.decode_function_input(input[data])  # function used to decode input, before you use it a contract object is necessary
                for i in range(len(input_result[1])):
                    if type(input_result[1][matched['inputs'][i]['name']]) == bytes or type(input_result[1][matched['inputs'][i]['name']]) == hexbytes.main.HexBytes:
                        matched['inputs'][i]["result"] = input_result[1][matched['inputs'][i]['name']].hex()
                    else: 
                        matched['inputs'][i]["result"] = input_result[1][matched['inputs'][i]['name']]
                        
                matched['function full name'] = str(input_result[0])
        
            else: 
                if type(input[data]) == hexbytes.main.HexBytes:  # convert byte type data into readable data type(usually convert to string)
                    matched[data] = input[data].hex()
                else: matched[data] = input[data]
        
        # time record of the end of decoding input
        self.Otimes.Nend0(timeit.default_timer())
        # time record of starting decoding logs 
        self.Otimes.Nstart1(timeit.default_timer())
        
        logs = event_checker(self.w3, receipt, self.ABI_file, self.event, self.file_name)
        logs.mapping(Otimes = self.Otimes)
        logs_info = logs.event_spliter()
        
        final = [matched]
        if len(logs_info) == 0:
            final.append({"logs" : "no matched logs"})
        else:
            final.append(logs_info)
            
        self.Otimes.Nend1(timeit.default_timer())
        
        # this two return value is a little stupid, because the second one is completely unrealted to data decode
        # the second step also force me comparmise in the Error return
        return final, self.Otimes.Ntotal()
    


def test(): 
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Your infra project"))
    tx_hash = "0x7e10f2288b2edf6d3e22d5a94cb24fcf1f1cd6cc60f20a7d4da451276485c3f8"
    written_path = "" + tx_hash + ".json"  # reset your path in the first ""
    
    jack = checker(w3, tx_hash)
    files, timer = jack.decode_tx_info()
    Abi_convert.abi_writer(written_path, files)
    
    
    # txs = block_tx(w3).blk_txs()
    # total : float = 0
    print("Times is: " + str(timer))

test()
