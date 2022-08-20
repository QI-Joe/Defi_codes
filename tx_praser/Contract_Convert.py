import HeaderFile as hf
import FreemanDB


EtherscanKey : str = "KCZFUVHX2EBKU1TRYN5NAI31KHTQSYNPRK"

class ContractConvert:
    abi : dict
    w3 = hf.Web3(hf.Web3.HTTPProvider("https://mainnet.infura.io/v3/e871b52e91224b89a26ce7aad3857819"))
    
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

    def abi_json_writer(self, abi_files, db):
        """basically this function will write events into database

        Args:
            abi_files (_type_): processed ABI files
        """
        db.insert_contract(abi_files)
        return
    
def w3ForkBuilder(contract : str):
    Links = "https://api.etherscan.io/api?module=contract&action=getabi&address={contract}&apikey={EtherscanKey}"
    abi = hf.basic_json.loads(hf.requests.get(Links).text)
    db = FreemanDB.DAIPoolDB()
    db.execute_sql_code('''DELETE FROM fi
DELETE FROM fo
DELETE FROM ce
DELETE FROM ei
DELETE FROM t
DELETE FROM tfi
DELETE FROM tf
DELETE FROM tfo
DELETE FROM tei
DELETE FROM cf''')
    fuckers = ContractConvert(abi)
    functions : dict = fuckers.adjustor()
    functions["contract_address"] = contract
    fuckers.abi_json_writer(functions, db)
    
    
if __name__ == "__main__":
    with open("", "r") as file:
        files = hf.basic_json.loads(file)
    for protocols in files:
        w3ForkBuilder("0x62629A1Fd652E7701DCF5362c2e2d91290575631")
    
