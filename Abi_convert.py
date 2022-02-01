import time
from web3 import Web3  
import requests
from ujson import json


global_mykey="Your Etherscan developer key"
ABI = object
file_address = object
wrong = {}
contract = None

def web3_provider_and_contract_source_code(Address):
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/your infra project code"))
    if  w3.isConnected == False:
        print("Web3 opening failed, check web3 connection")
        return None
    Address=Web3.toChecksumAddress(Address)
    contract = w3.eth.contract(address=Address, abi= ABI["result"])
    decode = contract.decode_function_input
    return w3, contract

def Abi_geter(Address):
    Address=Web3.toChecksumAddress(Address)
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
        if bracket["type"] == "function":
            contract_checker(bracket)
    return result

def abi_writer(input_path, abi_files, files_name):
    path=input_path + files_name + ".json"
    with open(path, 'w') as final_step:
        json.dump(abi_files, final_step, ensure_ascii=False, indent=4)
    final_step.close()
    return

def contract_checker(parenthetical):  # do we really need this ? You can check web3 file /python3.10/Lib/site-packages/eth_abi/abi
    global contract
    if contract is None:
        w3, contract = web3_provider_and_contract_source_code(file_address)
    try:
        if not contract.get_function_by_selector(parenthetical["signature"]):  # can we simplify there ?
            parenthetical = format_exchange(parenthetical)
            wrong[parenthetical["name"]] = parenthetical
            parenthetical["stauts"] = "cannot match with Etherscan"
    except ValueError:
        parenthetical["status"] = "Etherscan doesnt record this function."
        

def main():
    global file_address 
    path = input("input your path: ")
    file_address = "0xc4269cc7acdedc3794b221aa4d9205f564e27f0d"  # this address will lead your to contract "Flapper"
    
    abi=Abi_geter("0xc4269cc7acdedc3794b221aa4d9205f564e27f0d")
    if  not abi:
        print("cannot get abi, exception occured.")
        return
    abi= ABI_adjustor(abi)
    if wrong:
        print("Unmatched method id occured, please go to json file to check later")
    abi_writer(path, abi, "0xc4269cc7acdedc3794b221aa4d9205f564e27f0d")  # remeber to add a backslash "/" in the last of your path
    # e.g D:/user/ABI_files/
main()

