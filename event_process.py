from concurrent.futures import process
import hexbytes
import logging
import web3.datastructures as structure
from web3._utils import events as parser
from times import time_longth
import web3_provider

class Event_checker:
    
    w3 = web3_provider.provider.w3_provider()
    Contract : dict
    receipt : structure.AttributeDict
    event : dict
    contract_address : str
    tempStore : dict
    
    Otimes : time_longth
    
    def __init__(self, receipt, Contract, event : dict, address:str) -> None:
        if receipt is None or Contract is None or event is None:
            print("invalid information/connection fails")
            exit()
        self.receipt = receipt
        self.Contract = Contract
        self.event = event
        self.contract_address = address
    
    def mapping(self, Otimes : time_longth):
        self.Otimes = Otimes
        return 
    
    
    # during codes running this function usually will cost most time
    # convert this function into multiprocess will greately optimize codes effience
    def assumble(self, logs:dict):
        matched_event : list = []
        # if __name__ == "__main__":
        #     with process.ProcessPoolExecutor(max_workers = 5) as executor:
        #         matched_event = executor.map(self.event_decoder, logs)
        for ievent in logs:  # this loop is used for single process running
            event_result = self.event_decoder(ievent)
            if not event_result: continue 
            matched_event.append(event_result)
        return matched_event 
       
    def event_decoder(self, event : dict):
        # if not web3_provider.contract_detect(event['address']):
        
        # custom emitted event will be ignored
        if event["topics"][0].hex()[10 :] == "00000000000000000000000000000000000000000000000000000000":
            return 0
        # retrieve if the coressponding ABI has been read or not
        if event['topics'][0].hex() not in self.event:
            new_event : dict = web3_provider.combine_tx(event['address'])
            try:
                # merge the two dict and update self.event
                self.event = {**self.event, **new_event['event']} 
            except TypeError: return #new_Abi_checker.test()
        
        try:
            result : dict = self.event[event['topics'][0].hex()].copy()
        except KeyError: 
            
            # in the last program wont raise any bugs or force program to stop if ABI can not matched with non cusomized event
            # will use logs to record the bug and jump through it.
            
            Rformat = "%(asctime)s - %(pathname)s - %(funcName)s - %(message)s"
            logging.basicConfig(filename= self.contract_address + ".log", filemode = "w", level = logging.DEBUG, format = Rformat)
            logging.debug('''web3 hasnt return corresponding event ABI. 
                target ABI address is: ''' + str(event['address']) + '\n' + 
                "target event signature is: " + str(event['topics'][0].hex()))
            return 0
        
        counterpart = parser.get_event_data(self.w3.codec, result, event)  # decode data by using web3
        
        counter_keys : list = ["transactionHash", "name", "signature", "type", "logIndex", "transactionIndex"]
        # first iteration, bascially we do the same with inputs
        for value in counterpart:  # insert processed input data into matched_event
            if value == 'args':
                # second iteration since result of get_event_data is more complex, its not a tuple
                for index in range(len(result['inputs'])):
                    pointer = result['inputs'][index]['name']
                    # store result
                    result['inputs'][index]['result'] = counterpart[value][pointer]
                    # add new items in both result, counter_keys
                    counter_keys.extend(["inputs" + str(index) + "_" + items for items in result["inputs"][index].keys()])
                    for dkey, dvalue in result['inputs'][index].items():
                        result["inputs" + str(index) + "_" + dkey] = dvalue.hex() if type(dvalue) == hexbytes.main.HexBytes or type(dvalue) == bytes else dvalue
            elif type(counterpart[value]) == hexbytes.main.HexBytes:
                result[value] = counterpart[value].hex()
            if value not in counter_keys and value not in ['inputs', 'args', 'event'] : 
                counter_keys.append(value)
            if value not in result.keys() and value != "event" and value != "args":
                result[value] = counterpart[value].hex() if type(counterpart[value]) == hexbytes.main.HexBytes or type(counterpart[value]) == bytes else counterpart[value]
        # since event decoder doesnt provide event full name, here we self revert the full name
        result['name'] = result['name'] + '(' + ",".join([result['inputs'][loops]['type'] + " "+ result['inputs'][loops]['name'] for loops in range(len(result['inputs']))]) + ')'
        result.pop("inputs")
        counter_keys.append("anonymous")
        result = dict(sorted(result.items(), key=lambda x: counter_keys.index(x[0])))
        
        # print(result['name'])
        return result
    
    def event_spliter(self):
        decoded_logs = {}
        for Nevent in self.receipt:
            if Nevent != 'logs':
                if type(self.receipt[Nevent]) == hexbytes.main.HexBytes:
                    decoded_logs[Nevent] = self.receipt[Nevent].hex()
                else: decoded_logs[Nevent] = self.receipt[Nevent]
            # actually, in the last only decoded_logs["logs"] been written into csv file, for other information will be ignored
            elif Nevent == 'logs':
                decoded_logs[Nevent] = self.assumble(self.receipt[Nevent])
        return decoded_logs

