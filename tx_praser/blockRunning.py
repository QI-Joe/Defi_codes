import HeaderFile as hf
import AbiChecker_Pandas as AO
import neWeb3 as nw

def fileRead():
    hashes : hf.pd.DataFrame = "d8e2fc689d230b77e831daee03f290d59eee98f0121f35f4f741a0fa2388a446"
    AO.starter(hashes.to_list())
    
fileRead()