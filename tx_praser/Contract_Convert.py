import HeaderFile as hf

class ContractConvert:
    abi : dict
    
    def __init__(self, abi : dict):
        self.abi = abi
    
    def function_hash(self, item:dict):
        if ('inputs' not in item.keys()):
            return 
        input_list = [input_item['type'] for input_item in item['inputs']]
        full_name = item['name'] + '(' + ','.join(input_list) + ')'
        fhash=hf.Web3.keccak(text = full_name)
        fhash=fhash.hex()
        return fhash
    
    def adjustor(self):
        if self.abi['message']!='OK' or (self.abi['result'] is None): 
            return False
        result = hf.basic_json.loads(self.abi['result'])
        functions, event  = {}, {}
        for bracket in result:
            if (bracket["type"] == "function"): 
                bracket["signature"] = self.function_hash(bracket)[0:10]
                functions[bracket["signature"]] = bracket
            elif (bracket["type"] == "event"): 
                bracket["signature"] = self.function_hash(bracket) 
                event[bracket["signature"]] = bracket
            else: bracket["signature"] = bracket["type"]
        return {"functions": functions, "event": event}
    
    