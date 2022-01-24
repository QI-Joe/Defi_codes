from time import time
from eth_typing import HexStr
from web3 import Web3
import pre_read

class checker:
    w3 = None
    my_key=None
    tx_hash=None
    mapper = None
    
    def __init__(self, w3, my_key, tx_hash) -> None:
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
        self.mapper = pre_read.pre_map()
        
    
    def get_tx(self) -> HexStr:
        tx = self.w3.eth.get_raw_transaction(self.tx_hash)
        tx = tx.hex()
        return tx    
    
    def parameters(self, variable, module) -> dict:
        for part in variable:
            print(type(part))
        return module
    
    def parse_rawtx(self) -> dict:
        tx= self.get_tx()
        signatures = tx[0:10]
        parameters = list()
        for i in range (0 < (len(tx)-10) / 64):
            parameters.append(tx[10+64*i : 10 + 64*(i+1)])
        module = self.mapper[signatures]
        self.mapper[signatures] = self.parameters(parameters, module)
        return self.mapper
        