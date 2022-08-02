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
    
    def assumble(self, logs:dict):
        matched_event : list = []
    # this loop is used for single process running
        for ievent in logs:  
            event_result = self.event_decoder(ievent)
            if not event_result: continue 
            matched_event.append(event_result)
        return matched_event 
       
    def event_decoder(self, event : dict):
        # simplfy there
        if event["topics"][0].hex()[10 :] == "00000000000000000000000000000000000000000000000000000000":
            new_event : dict = self.w3.combine_tx(event['address'])
            self.func = new_event["functions"]
            try:
                print(event["topics"][0].hex()[ :10], event["topics"][0].hex()[ :10] in self.func)
                matchedInput: hf.Any = self.func[event["topics"][0].hex()[ :10]]
            except KeyError: return 0    
            inpuEvent: dict = self.camouflage(matchedInput, event)
            event = inpuEvent["ChengedEvent"]
            self.event = {**{event["topics"][0].hex() :inpuEvent["digused ABI"].copy()}, **self.event}
        # retrieve if the coressponding ABI has been read or not
        elif event['topics'][0].hex() not in self.event:
            new_event : dict = self.w3.combine_tx(event['address'])
            try:
                # merge the two dict and update self.event
                self.event = {**self.event, **new_event['event']} 
            except TypeError: return 
        
        try:
            result : dict = self.event[event['topics'][0].hex()].copy()
        except KeyError: 
            # in the last program wont raise any bugs or force program to stop if ABI can not matched with non cusomized event
            # will use logs to record the bug and jump through it.
            Rformat = "%(asctime)s - %(pathname)s - %(funcName)s - %(message)s"
            hf.logging.basicConfig(filename= self.contract_address + ".log", filemode = "w", level = hf.logging.DEBUG, format = Rformat)
            hf.logging.debug('''web3 hasnt return corresponding event ABI. \n
                target ABI address is: ''' + str(event['address']) + '\n' + 
                "target event signature is: " + str(event['topics'][0].hex()))
            return 0
        
        counterpart = hf.parser.get_event_data(self.w3._w3_geter().codec, result, event)  # decode data by using web3
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
        if not (Postart-1) % 64: return False
        return True
    
    def indexed_marker(self, totalData: list, indexedList: list, input_ABI: list):
        for indexed in range(len(indexedList)):
            if indexedList[indexed] in totalData:
                input_ABI[indexed]['indexed'] = True
    
    def camouflage(self, func_ABI: dict, target: hf.structure.AttributeDict):
        # read the standard format of event 
        if self.template == None:
            with open(r"D:/pycharm/simulate/ABI_files/Event_standard_format.json", 'r') as tarfile:
                self.template = hf.json.load(tarfile)
            # tarfile.close()
        standrformat: dict = hf.copy.deepcopy(self.template)
        vaLength: int
        # set standard format as basement, access in it
        for key, value in standrformat.items():
            # import some necessary first layer key value
            if key!= "inputs" and key in func_ABI.keys():
                standrformat[key] = func_ABI[key]
            # merge value in inputs to standard template of event
            if key == "inputs":
                inlogs: list = func_ABI["inputs"] 
                vaLength = len(inlogs)
                for invalue in inlogs:
                    # dict in value[0] wont be overwriteen instead it always been set as template
                    inpuTemplate: dict = value[0].copy()
                    # merge value with same key in both dicts in dict layer to keep code concise
                    # this expression only suit for python 3.5+, for detail you can refer to
                    # https://stackoverflow.com/questions/71546879/how-to-assign-value-in-dict1-to-dict2-if-the-key-are-the-same-without-loop
                    inpuTemplate = {**inpuTemplate, **invalue}
                    inpuTemplate["internalType"] = invalue["type"]
                    # value is target(receipt)['logs]['inputs'], which is a list
                    value.append(inpuTemplate)
                # in the last we delete the template value[0]
                del value[0]
        # second step, change item topics and data in target
        topics: list = [topic.hex()[2: ] for topic in target['topics']]
        Postart: int = target['data'].find(topics[0][: 8]) + 8
        if not self.position_checker(Postart):
            # later add a function to skip the part and record it into logs
            raise ValueError("there is similar singature appear, check the status.")
        trueInput: list = [target['data'][Postart+tarval*64 : Postart + 64* (tarval+1)] for tarval in range(vaLength)]
        indexed: list = [trueInput[indexedval] for indexedval in range(len(trueInput)) if trueInput[indexedval] in topics and indexedval<3]
        # rerturn type of event_abi_to_log_topic has already been hexbytes type 
        standrformat["type"] = "event"
        target = dict(target)
        target['topics'] = list(map(hf.hexbytes.main.HexBytes, [hf.tools.event_abi_to_log_topic(standrformat)] + indexed))
        self.indexed_marker(trueInput, indexedList = indexed, input_ABI = standrformat['inputs'])
        # restore the data part.
        differenceInput: list = [trueInput[Nval] for Nval in range(len(trueInput)) if trueInput[Nval] not in indexed or Nval+1>len(indexed)]  #set(trueInput).symmetric_difference(set(indexed))
        # disguise data type, from dict to structure.AttributeDict
        target['data'] = "0x" + ''.join(map(str, differenceInput))
        target = hf.structure.AttributeDict(target)
        return {"digused ABI" : standrformat, "ChengedEvent": target, "indexedPar" : indexed}
    
    def event_spliter(self):
        target = self.assumble(self.receipt["logs"])
        return target

