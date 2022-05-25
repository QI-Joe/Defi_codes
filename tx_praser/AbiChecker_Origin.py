from distutils.log import info
import HeaderFile as hf
from times import time_length
import web3_provider
from event_process import Event_checker

# main workflow of this program
class Checker:
    w3provider = web3_provider.provider
    w3 = w3provider.w3_provider()
    tx_hash : str
    aggrCon : dict
    
    Otimes = time_length()
    
    def __init__(self, tx_hash) :
        while tx_hash is None:
            print("Havent received any valid transaction hash, please input again")
            tx_hash = input("tx_hash: ")
        self.tx_hash=tx_hash
    
    # will using multiprocessing to faster the programming
    def total_console(self):
        # for future in concurrent.futures.as_completed():
        # using multithreading to accelerate the I/O part
        with hf.Thruser.ThreadPoolExecutor(max_workers=2) as executor:
            tx : hf.Future = executor.submit(self.w3.eth.get_transaction, self.tx_hash)
            receipt : hf.Future = executor.submit(self.w3.eth.get_transaction_receipt, self.tx_hash)
        self.decode_tx_input(tx.result())
        self.decode_tx_event(receipt.result())
        return 
    
    # used to decode input
    def decode_tx_input(self, tx_input : hf.structure.AttributeDict) :
        # used to test decode_tx_input running time
        func_name = hf.sys._getframe().f_code.co_name
        if type(func_name) != str:
            func_name = str(func_name)
        self.aggrCon = web3_provider.combine_tx(tx_input["to"]) 
        if not self.aggrCon: 
            # write a log input for message must be tuple
            web3_provider.LOGWriter("txs", txmsg = (tx_input.hash.hex(), ) )
            return
        contract = web3_provider.provider.contract_factory_provider()  # according to its source code, this actually run in local
        matched = None
        try:
            matched = self.aggrCon["functions"][tx_input['input'][0:10]].copy()
        except KeyError:
            return False
        if matched == None: 
            print("input cannot match with current ABI files")
            return False
        # reorder matched keys    
        keyW: list = ["hash", "function full name", "signature", "from", "to", "blockNumber"]
        # first iteration
        for data in tx_input:
            if data == 'input':
                input_result = contract.decode_function_input(tx_input[data])
                for inputs_index in range(len(input_result[1])):
                    matched['inputs'][inputs_index]['result'] = input_result[1][matched['inputs'][inputs_index]['name']]
                    keyW.extend(["inputs" + str(inputs_index) + "_" + item_name for item_name in matched["inputs"][inputs_index].keys()])
                    for dkey, dvalue in matched['inputs'][inputs_index].items():
                        matched["inputs" + str(inputs_index) + "_" + dkey] = dvalue.hex() if type(dvalue) == hf.hexbytes.main.HexBytes or type(dvalue) == bytes else dvalue
                matched['function full name'] = str(input_result[0])
            else: 
                if type(tx_input[data]) == hf.hexbytes.main.HexBytes:
                    matched[data] = tx_input[data].hex()
                else: matched[data] = tx_input[data]
                if data not in keyW: keyW.append(data)
        try:
            for accessEle in range(len(matched["accessList"])):
                matched["accessList" + str(accessEle)] = matched["accessList"]
                keyW.append("accessList" + str(accessEle))
        except KeyError: pass
        # this for loop used to change format to convient the write of csv
        for output in matched["outputs"]:
            matched["outpus_name"] = output["name"]
            matched["outpus_type"] = output["type"]
            keyW.insert(keyW.index('maxFeePerGas') , "outpus_name")
            keyW.insert(keyW.index('outpus_name') + 1, "outpus_type")
        matched.pop("outputs", None)
        matched.pop("inputs", None)
        matched.pop("name", None)
        matched.pop("accessList", None)
        keyW.extend(list(set(matched.keys()) - set(keyW)))
        # reorder the dict
        matched = dict(sorted(matched.items(), key=lambda x: keyW.index(x[0])))
        # since for beauty we dont store input and event in the same csv files, after we finsih parse input we can directly write to corresponding csv file
        # the specified path be like: D:/pycharm/simulate/ABI_files/tx_hash_input.csv
        web3_provider.abi_csv_writer(self.w3provider.csvPath("tx_input"), [matched])
        
    # used to decode event
    def decode_tx_event(self, receipt : hf.structure.AttributeDict):
        if not self.aggrCon: return False
        logs = Event_checker(receipt, self.aggrCon["functions"], self.aggrCon["event"], self.aggrCon["contract_address"])
        logs_info = logs.event_spliter()
        web3_provider.abi_csv_writer(self.w3provider.csvPath("txs_events"), logs_info)
    
def starter(blk: int):
    txList = Checker.w3.eth.get_block(blk).transactions
    for tx in txList:
        JackThr: Checker = Checker(tx.hex())
        JackThr.total_console()
    print("Block {blk} finished process")
    return True
   