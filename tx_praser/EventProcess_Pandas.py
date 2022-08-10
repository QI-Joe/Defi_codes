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
            if not event_result: continue 
            matched_event.append(event_result)
        return matched_event 
       
    def event_decoder(self, event : dict):
        """decode logs in event

        Args:
            event (dict): logs raw info from Ethereum API

        Returns:
            boolean: true or not the programming running normally
        """
        # simplfy there
        if event["topics"][0].hex()[10 :] == "0" * 56:
            new_event : dict = self.w3.combine_tx(event['address'])
            self.func = new_event["functions"]
            try:
                matchedInput: hf.Any = self.func[event["topics"][0].hex()[ :10]]
            except KeyError: return False    
            inpuEvent: dict = self.camouflage(matchedInput, event)
            event = inpuEvent["ChengedEvent"]
            self.event = {event["topics"][0].hex() : inpuEvent["digused ABI"]}
        # retrieve if the coressponding ABI has been read or not
        elif event['topics'][0].hex() not in self.event:
            self.event : dict = self.w3.combine_tx(event['address'])
        
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
        return True
    
    def position_checker(self, Postart: int):
        if not (Postart-1) % 64 or Postart == 7: return False
        return True
    
    def indexed_marker(self, trueInput: list, indexedList: list, input_ABI: list):
        for indexed in range(len(indexedList)):
            if indexedList[indexed] in trueInput:
                input_ABI[indexed]['indexed'] = True
    
       
    def camouflage(self, func_ABI: dict, target: hf.structure.AttributeDict):
        """
        merge value with same key in both dicts in dict layer to keep code concise
        this expression only suit for python 3.5+, for detail you can refer to
        https://stackoverflow.com/questions/71546879/how-to-assign-value-in-dict1-to-dict2-if-the-key-are-the-same-without-loop
        
        Args:
            func_ABI is matchedInput from line39, mainly stores ABI without info data
            target is logs with input info
                
        Return:
            dict contain modified decodable ABI and receipt
            
        Raises:
            ValueError
        """
        if self.template == None:
            with open(r"D:/pycharm/simulate/ABI_files/Event_standard_format.json", 'r') as tarfile:
                self.template = hf.json.load(tarfile)
        func_ABI["type"] = "event"
        func_ABI["inputs"][ : ] = [{**self.template["inputs"][0], **value} for value in func_ABI["inputs"]]
        func_ABI = {**self.template, **func_ABI}
        vaLength = len(func_ABI["inputs"])
        
        topics: list = [topic.hex()[2: ] for topic in target['topics']]
        Postart: int = target['data'].find(topics[0][: 8]) + 8
        if not self.position_checker(Postart):
            # later add a function to skip the part and record it into logs
            raise ValueError("there is similar singature appear, check the status.")
        trueInput: list = [target['data'][Postart+tarval*64 : Postart + 64* (tarval+1)] for tarval in range(vaLength)]
        target = target.__dict__
        
        target['topics'] = list(map(hf.hexbytes.main.HexBytes, [hf.tools.event_abi_to_log_topic(func_ABI)] + topics[1:]))
        
        self.indexed_marker(trueInput, indexedList = topics[1:], input_ABI = func_ABI['inputs'])
        data: list = [val
                          for val in trueInput 
                          if val not in topics[1:]]  
        target['data'] = "0x" + ''.join(map(str, data))
        target = hf.structure.AttributeDict(target)
        return {"digused ABI" : func_ABI, "ChengedEvent": target}
    

