import HeaderFile as hf
import AbiChecker_Pandas as AP
import neWeb3 as nw

# how to convert timestamp to date: https://ethereum.stackexchange.com/questions/7287/how-to-find-the-date-of-an-ethereum-transaction-while-parsing-it-with-web3 
# w3 = nw.W3()._w3_geter
# block number in (2022, 2, 23, 23, 36, 21), sereval hours before Ukranie and Russian war
initialBlk : int = 14277036
# Currentblk : int = w3.eth.get_block("latest")

def fileRead():
    hashes : hf.pd.DataFrame = ["0xd8e2fc689d230b77e831daee03f290d59eee98f0121f35f4f741a0fa2388a446"]
    AP.starter(hashes)
    
fileRead()