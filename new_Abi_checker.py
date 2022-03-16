from queue import Queue
import hexbytes
from web3 import Web3
import timeit
import web3_provider
from event_process import Event_checker
from times import time_longth, block_tx
import web3.datastructures as structure
import multiprocessing as process


# main workflow of this program
class Checker:
    w3 = web3_provider.provider.w3_provider()
    tx_hash : str
    aggrCon : dict
    
    path : str = ".\ABI_files"
    
    Otimes = time_longth()
    
    def __init__(self, tx_hash) :
        while tx_hash is None:
            print("Havent received any valid transaction hash, please input again")
            tx_hash = input("tx_hash: ")
        self.tx_hash=tx_hash
        
    def file_get(self, Address : str) :  # Address in there has been checked
       # if not pre_read.contract_detect(self.path + Address + ".json"): 
        self.aggrCon = web3_provider.combine_tx(Address)
        if not self.aggrCon["event"]: return 
        self.aggrCon["contract_address"] = Web3.toChecksumAddress(self.aggrCon["contract_address"]) 
    
    # will using multiprocessing to faster the programming
    def total_console(self):
        tx = self.w3.eth.get_transaction(self.tx_hash)  # this step cost the longest time
        receipt = self.w3.eth.get_transaction_receipt(self.tx_hash)
        self.file_get(Web3.toChecksumAddress(tx['to']))
        #------------- waiting for adjustment
        keeper = Queue()                     # need to be rewrite as Process.Queue()
        #------------- waiting for adjustment
        self.decode_tx_input(tx, keeper)
        self.decode_tx_event(receipt, keeper)
        
        #------------- waiting for adjustment
        # keeper = process.Queue()
        # p1 = process.Process(target = self.decode_tx_input, args = (tx, keeper, ))
        # p2 = process.Process(target = self.decode_tx_event, args = (receipt, keeper, ))
        # if __name__ == "__main__":
        #     p1.start()
        #     p2.start()
        #     p1.join()
        #     p2.join()
        #------------- waiting for adjustment
        
        # result = keeper.get()
        return 
    
    
    # used to decode input
    def decode_tx_input(self, tx_input : structure.AttributeDict, keeper : Queue) :
        self.Otimes.Nstart0(timeit.default_timer())
        
        web3_provider.provider.Abi_Get(self.aggrCon["contract_address"], {"result" : self.aggrCon["ABI_files"]})
        contract = web3_provider.provider.contract_factory_provider()  # according to its source code, this actually run in local
        matched = None
        
        try:
            matched = self.aggrCon["functions"][tx_input['input'][0:10]]
        except KeyError:
            return 0, False
        
        if matched == None: 
            print("input cannot match with current ABI files")
            return 0, False
        
        # reorder matched keys    
        keyW: list = ["hash", "function full name", "signature", "from", "to", "blockNumber"]
        
        # first iteration
        for data in tx_input:
            if data == 'input':
                input_result = contract.decode_function_input(tx_input[data])
                # second iteration, specificly build for inputs
                for inputs_index in range(len(input_result[1])):
                    # write inputs[index] result into matched
                    # input_result is a 2-length tuple generate by contract.decode_function_input
                    # first line record inputs full name like <mint(address usr, int64 value)>, second record decoded input result
                    matched['inputs'][inputs_index]['result'] = input_result[1][matched['inputs'][inputs_index]['name']]
                    # add new key for sort
                    keyW.extend(["inputs" + str(inputs_index) + "_" + item_name for item_name in matched["inputs"][inputs_index].keys()])
                    # add new item to record the same value in inputs
                    for dkey, dvalue in matched['inputs'][inputs_index].items():
                        matched["inputs" + str(inputs_index) + "_" + dkey] = dvalue.hex() if type(dvalue) == hexbytes.main.HexBytes or type(dvalue) == bytes else dvalue
                matched['function full name'] = str(input_result[0])
            # add other non indent value in matched
            else: 
                if type(tx_input[data]) == hexbytes.main.HexBytes:
                    matched[data] = tx_input[data].hex()
                else: matched[data] = tx_input[data]
                if data not in keyW: keyW.append(data)
        # value of accessList is a list, algouth most of times its an empty list, here we still 
        # set a loop in case of accident. but disadvantage here is that if one day accessList has its own value,
        # it wont be written into matched since its an empty list
        for accessEle in range(len(matched["accessList"])):
            matched["accessList" + str(accessEle)] = matched["accessList"]
            keyW.append("accessList" + str(accessEle))

        # this for loop used to change format to convient the write of csv
        for output in matched["outputs"]:
            matched["outpus_name"] = output["name"]
            matched["outpus_type"] = output["type"]
            keyW.insert(keyW.index('maxFeePerGas') , "outpus_name")
            keyW.insert(keyW.index('outpus_name') + 1, "outpus_type")
        # delete some with indent items to keep plain of dict
        matched.pop("outputs", None)
        matched.pop("inputs", None)
        matched.pop("name", None)
        # accessList been deleted, but easy to cause bug
        matched.pop("accessList", None)
        
        # add the value that doesnt stored in keyW compare with matched
        keyW.extend(list(set(matched.keys()) - set(keyW)))
        # reorder the dict by elements order in keyW
        matched = dict(sorted(matched.items(), key=lambda x: keyW.index(x[0])))
        # stop recording running time of decode input
        self.Otimes.Nend0(timeit.default_timer())
        # since for beauty we dont store input and event in the same csv files, after we finsih parse input we can directly write to corresponding csv file
        # the specified path be like: D:/pycharm/simulate/ABI_files/tx_hash_input.csv
        web3_provider.abi_csv_writer(self.path + "\tx_input.csv", [matched])
        # store in Queue, this queue is prepared for multiprocessing
        # keeper.put(matched)
        
    # used to decode event
    def decode_tx_event(self, receipt : structure.AttributeDict, keeper : Queue):
        self.Otimes.Nstart1(timeit.default_timer())
        # if we cant get 
        if not self.aggrCon["event"]: return False,  False
        logs = Event_checker(receipt, self.aggrCon["ABI_files"], self.aggrCon["event"], self.aggrCon["contract_address"])
        logs.mapping(Otimes = self.Otimes)
        logs_info = logs.event_spliter()
        # matched : list = []
        if len(logs_info) == 0:
            logs_info["logs"] = 0
        web3_provider.abi_csv_writer(self.path + "\txs_events.csv", logs_info['logs'])
        self.Otimes.Nend1(timeit.default_timer())
        # keeper.put(matched)
        

def test(): 
    tx_hash = "0x8a7a6774e8cde45975941f5dd3151439b272f66900b210f9700ec5fbac3aa7db"
    written_path = "" + tx_hash + ".json"  # reset your path in the first ""
    jack = Checker(tx_hash)
    files = jack.total_console()
    
test()
