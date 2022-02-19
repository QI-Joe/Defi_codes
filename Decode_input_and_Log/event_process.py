from tokenize import String
from typing import Dict
import hexbytes
import web3 as Web3
import pre_read
from web3._utils import events as parser
from Abi_convert import combine_tx
from times import time_longth
import timeit

class event_checker:
    
    w3 : Web3.HTTPProvider
    Contract = None
    receipt = None
    event = None
    contract_address = None
    tempStore : dict
    
    Otimes : time_longth
    
    def __init__(self, w3, receipt, Contract, event : dict, address:String) -> None:
        if receipt is None or Contract is None or event is None:
            print("invalid information/connection fails")
            exit()
        self.w3 = w3
        self.receipt = receipt
        self.Contract = Contract
        self.event = event
        self.contract_address = address
    
    def mapping(self, Otimes : time_longth):
        self.Otimes = Otimes
        return 
    
    def assumble(self, logs:Dict):
        result = dict
        matched_event = []
        for event in logs:
            
            # if in local file there isnt a corresponding contract, program will try to download it from etherscan 
            if not pre_read.contract_detect(event['address']):
                combine_tx(event['address'], 2)
            
            if event['address'] != self.contract_address or self.event is None:  # get correct contract ABI
                
                self.Otimes.Nstart2(timeit.default_timer())
                new_event, _, new_abi, _ = pre_read.reader(event['address'] + '.json').pre_map()
                self.Otimes.Nend2(timeit.default_timer())
                
                if not new_event: continue
                self.event = {**self.event, **new_event}  # merge the two dict and update self.event
            
            try:
                result = self.event[event['topics'][0].hex()]
            except KeyError: continue
            
            matched_event.append(result)
            result = parser.get_event_data(self.w3.codec, matched_event[-1], event)  # decode data by using web3
            
            for value in result:  # insert processed input data into matched_event
                if value == 'args':
                    for i in range(len(matched_event[-1]['inputs'])):
                        pointer = matched_event[-1]['inputs'][i]['name']
                        matched_event[-1]['inputs'][i]['result'] = result[value][pointer]
                elif type(result[value]) == hexbytes.main.HexBytes:
                    matched_event[-1][value] = result[value].hex()
                elif value == 'event': 
                    print(result["event"])
                    continue
                else: matched_event[-1][value] = result[value]
            
        return matched_event
    
    def event_spliter(self):
        decoded_logs = {}
        for i in self.receipt:
            if i != 'logs':
                if type(self.receipt[i]) == hexbytes.main.HexBytes:
                    decoded_logs[i] = self.receipt[i].hex()
                else: decoded_logs[i] = self.receipt[i]
            elif i == 'logs':
                decoded_logs[i] = self.assumble(self.receipt[i])
                
        return decoded_logs

