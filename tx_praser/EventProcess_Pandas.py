import HeaderFile as hf
import neWeb3 as w3

class Event_checker:
    w3 = w3.W3()
    event : dict # receive ABI
    func: dict   # receive ABI
    template: dict = None
    receipt : hf.structure.AttributeDict
    contract_address : str
    
    def __init__(self, receipt, func: dict, event : dict):
        if event is None or func is None:
            print("invalid information/connection fails")
            exit()
        self.receipt = receipt
        self.func = func
        self.event = event
        return
    
    def assumble(self):
        matched_event : list = []
    # this loop is used for single process running
        for ievent in self.receipt["logs"]:  
            event_result = self.event_decoder(ievent)
            if event_result is not False: continue 
            matched_event.append(event_result)
        return matched_event 
       
    def event_decoder(self, event : dict):
        # simplfy there
        if event["topics"][0].hex()[10 :] == "00000000000000000000000000000000000000000000000000000000":
            new_event : dict = self.w3.combine_tx(event['address'])
            self.func = new_event["functions"]
            try:
                matchedInput: hf.Any = self.func[event["topics"][0].hex()[ :10]]
            except KeyError: return False    
            inpuEvent: dict = self.camouflage(matchedInput, event)
            event = inpuEvent["ChengedEvent"]
            self.event = {**{event["topics"][0].hex() :inpuEvent["digused ABI"].copy()}, **self.event}
        # retrieve if the coressponding ABI has been read or not
        elif event['topics'][0].hex() not in self.event:
            new_event : dict = self.w3.combine_tx(event['address'])
            try:
                # merge the two dict and update self.event
                self.event = {**self.event, **new_event['event']} 
            except TypeError: return False
        
        try:
            result : dict = self.event[event['topics'][0].hex()].copy()
        except KeyError: 
            w3.LOGWriter(Ltype="Logs", Logs=(str(event['address']), str(event['topics'][0].hex())))
            return False
        
        counterpart = hf.parser.get_event_data(self.w3._w3_geter().codec, result, event) 
        
        counterpart = {key : (value.hex()
        if type(value) is hf.hexbytes.main.HexBytes else value) 
        for key, value in counterpart.items()}
        
        for index in range(len(result['inputs'])):
            pointer = result['inputs'][index]['name']
            result['inputs'][index]['result'] = (counterpart["args"][pointer].hex()
            if isinstance(counterpart["args"][pointer], hf.hexbytes.main.HexBytes) or isinstance(counterpart["args"][pointer], bytes)
            else counterpart["args"][pointer])
        del counterpart["args"]
        
        result = (hf.pd.json_normalize({**result, **counterpart}, max_level=3)
        .apply(hf.pd.Series.explode)
        .reset_index()
        )
        target = hf.pd.json_normalize(result["inputs"], sep=".")
        result: hf.pd.DataFrame = hf.pd.concat([result.drop(columns = "inputs"), target], axis=1)
        
        result.to_csv("ABI_FIle_generator/CSVfiles/txs_events.csv",
        mode = "a",
        index = False,
        header = False if not hf.os.stat("ABI_FIle_generator/CSVfiles/txs_events.csv").st_size else True)
        return result
    
    def position_checker(self, Postart: int):
        if not (Postart-1) % 64 or Postart == 7: return False
        return True
    
    def indexed_marker(self, totalData: list, indexedList: list, input_ABI: list):
        for indexed in range(len(indexedList)):
            if indexedList[indexed] in totalData:
                input_ABI[indexed]['indexed'] = True
    
        """
        @args func_ABI is matchedInput from line39, mainly stores ABI without info data
        @args target is logs with input info
        
        merge value with same key in both dicts in dict layer to keep code concise
        this expression only suit for python 3.5+, for detail you can refer to
        https://stackoverflow.com/questions/71546879/how-to-assign-value-in-dict1-to-dict2-if-the-key-are-the-same-without-loop
        """
        """
        for value in func_ABI["inputs"]:
            value = {**self.template["inputs"][0], **value}
        """
    def camouflage(self, func_ABI: dict, target: hf.structure.AttributeDict):
        if self.template == None:
            with open(r"Event_standard_format.json", 'r') as tarfile:
                self.template = hf.json.load(tarfile)
        func_ABI["inputs"][ : ] = [{**self.template["inputs"][0], **value} for value in func_ABI["inputs"]]
        func_ABI = {**self.template, **func_ABI}
        vaLength = len(func_ABI["inputs"])
        
        # second step, change item topics and data in target
        topics: list = [topic.hex()[2: ] for topic in target['topics']]
        Postart: int = target['data'].find(topics[0][: 8]) + 8
        if not self.position_checker(Postart):
            # later add a function to skip the part and record it into logs
            raise ValueError("there is similar singature appear, check the status.")
        trueInput: list = [target['data'][Postart+tarval*64 : Postart + 64* (tarval+1)] for tarval in range(vaLength)]
        indexed: list = [trueInput[indexedval] for indexedval in range(len(trueInput)) if trueInput[indexedval] in topics and indexedval<3]
        # rerturn type of event_abi_to_log_topic has already been hexbytes type 
        func_ABI["type"] = "event"
        target = target.__dict__
        target['topics'] = list(map(hf.hexbytes.main.HexBytes, [hf.tools.event_abi_to_log_topic(func_ABI)] + indexed))
        self.indexed_marker(trueInput, indexedList = indexed, input_ABI = func_ABI['inputs'])
        # restore the data part.
        differenceInput: list = [trueInput[Nval] for Nval in range(len(trueInput)) if trueInput[Nval] not in indexed or Nval+1>len(indexed)]  
        target['data'] = "0x" + ''.join(map(str, differenceInput))
        target = hf.structure.AttributeDict(target)
        return {"digused ABI" : func_ABI, "ChengedEvent": target, "indexedPar" : indexed}
    

