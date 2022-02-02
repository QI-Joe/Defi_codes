from tokenize import String
import web3 as Web3
import pre_read

class event_checker:
    
    w3 = None
    Contract = None
    receipt = None
    matched = None
    contract_address = None
    
    def __init__(self, w3, receipt, Contract, marched : dict, address:String) -> None:
        if receipt is None or Contract is None or marched is None:
            print("invalid information/connection fails")
            exit()
        self.w3 = w3
        self.receipt = receipt
        self.Contract = Contract
        self.matched = marched
        self.contract_address = address
    
    def assumble(self, logs: dict):
        result = dict
        matched = None
        for event in logs:
            if event['address'] != self.contract_address or self.matched is None:
                new_event, _, new_abi, _ = pre_read.reader("/" + event['address'] + '.json').pre_map()
                new_contract = self.w3.eth.contract(address = event['address'], abi = new_abi)
                result = new_contract.events[event['name']].processReceipt(self.receipt)
                matched = new_event[event['topic'][0]]
            else:
                result = self.Contract.events[event['name']].processReceipt(self.receipt)
            # insert processed input data into matched
            
        return matched
    
    def event_spliter(self):
        for i in self.receipt:
            if i != 'logs':
                self.matched[i] = self.receipt[i]
            elif i == 'logs':
                self.assumble(i)

                
