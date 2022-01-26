from ctypes import cast
from time import time
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
import pre_read  
import sys
sys.path.append("/python3.10/Lib/site-packages/web3/_utils")
import abi  # can be accessed and used
sys.path.append("/python3.10/Lib/site-packages/eth_abi")
import codec   # can be accessed but hard to be used

class checker:
    w3 = None
    my_key=None
    tx_hash=None
    mapper = None
    path = None
    
    def __init__(self, path, w3, my_key, tx_hash) -> None:
        if w3 is None: 
            print("connection fails, please check it. program will stop in 3 seconds")
            time.sleep(3)
            exit(ValueError)
        self.w3=w3
            
        while tx_hash is None:
            print("Havent received any valid transaction hash, please input again")
            tx_hash = input("tx_hash: ")
        self.tx_hash=tx_hash
        
        self.my_key=my_key
        self.mapper = pre_read.reader().pre_map()
        
    
    def get_tx(self) -> HexStr:
        tx = self.w3.eth.get_transaction(self.tx_hash)['input']
        return tx    
    
    def parameters(self, variable, module) :
        variable = HexBytes(variable)
        types = abi.get_abi_input_types(module)
        
        decoded = codec.ABIDecoder.decode_abi(types, cast(HexBytes, variable))  # next stage need to be implemented
        return decoded
    
    def parse_rawtx(self) -> dict:
        tx= self.get_tx()
        signatures = tx[0:10]
        parameters = tx[10 : ]
        module = self.mapper[signatures]
        self.mapper[signatures] = self.parameters(parameters, module)
        return self.mapper
        
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Your Project"))
path = input("input your json file path here: ")   #or you can skip this step and directly set your path
jack = checker( path, w3, "Your Ethereum Key", "0x854ee8eef97da539b67cd7c9dd09c408688aa1de26d38f4dc25aaa7d052c8cc6")
# 0x854ee8eef97da539b67cd7c9dd09c408688aa1de26d38f4dc25aaa7d052c8cc6 is a transaction hash
print(jack.parse_rawtx())