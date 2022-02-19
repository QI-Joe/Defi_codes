import string
from web3 import Web3  # if your wanna use this package, please google it, becasue it need you download a C++ maker first.
import requests
import json


global_mykey=""
ABI = object
file_address = object
wrong = {}
contract = None

def web3_provider_and_contract_source_code(Address):
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Your infra project"))
    if  w3.isConnected == False:
        print("Web3 opening failed, check web3 connection")
        return None
    Address=Web3.toChecksumAddress(Address)
    contract = w3.eth.contract(address=Address, abi= ABI["result"])
    return w3, contract

def Abi_geter(Address):
    # Address=Web3.toChecksumAddress(Address)
    if Address is None: return False
    ABI_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={Address}&apikey={global_mykey}"
    Abi=json.loads(requests.get(ABI_endpoint).text)
    if Abi is None: return False
    global  ABI
    ABI=Abi
    return Abi

def function_hash(item:dict):
    if ('inputs' not in item.keys()):
        return
    input_list = [input_item['type'] for input_item in item['inputs']]
    full_name = item['name'] + '(' + ','.join(input_list) + ')'
    fhash=Web3.keccak(text = full_name)
    fhash=fhash.hex()
    return fhash

def format_exchange(parenthetical):
    if (parenthetical["type"] == "function"): parenthetical["signature"] = function_hash(parenthetical)[0:10]
    elif (parenthetical["type"] == "event"): parenthetical["signature"] =   function_hash(parenthetical)  #  event_hash(parenthetical["name"])
    else: parenthetical["signature"] = parenthetical["type"]
    return parenthetical 

def ABI_adjustor(Abi):
    if Abi['message']!='OK' or (Abi['result'] is None): 
        return False
    result = json.loads(Abi['result'])
    for bracket in result:
        bracket = format_exchange(bracket)
    return result

def abi_writer(input_path, abi_files):
    path=input_path
    with open(path, 'w') as final_step:
        json.dump(abi_files, final_step, ensure_ascii=False, indent=4)
    final_step.close()
    return

def contract_checker(parenthetical):
    global contract
    if contract is None:
        _, contract = web3_provider_and_contract_source_code(file_address)
    try:
        if not contract.get_function_by_selector(parenthetical["signature"]):  # can we simplify there ?
            parenthetical = format_exchange(parenthetical)
            wrong[parenthetical["name"]] = parenthetical
            parenthetical["stauts"] = "cannot match with Etherscan"
    except ValueError:
        parenthetical["status"] = "Etherscan doesnt record this function."
        

# type in there means, if input is 1, which means variable hash is a tx hash
# tx hash dont need to be Checked
# but if type input is 2, it means input is a contract hash and contract hash need to be checked

def combine_tx(hash : string, type : int):
    path : string= "D:/pycharm/simulate/ABI_files/" + hash + ".json"
    if type == 2: hash = Web3.toChecksumAddress(hash)
    abi : dict = Abi_geter(hash)
    abi = ABI_adjustor(abi)
    abi_writer(path, abi)
    return

