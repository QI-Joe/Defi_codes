from web3 import Web3

class time_longth:
    
    start0: float
    end0:float
    start1:float
    end1:float
    start2:float = 0.0
    end2:float = 0.0
    
    Treceipt : float
    Tx : float
    
    def Nstart0(self, start0:float):
        self.start0 = start0
        return
    
    def Nend0(self, end0:float):
        self.end0 = end0
        return
    
    def Nstart1(self, start1:float):
        self.start1 = start1
        return
    
    def Nend1(self, end1:float):
        self.end1 = end1
        return
    
    def Nstart2(self, start2:float):
        self.start2 = start2
        return
    
    def Nend2(self, end2:float):
        self.end2 = end2
        return
    
    def Ntotal(self) -> float:
        return self.end0 - self.start0 + self.end1 - self.start1 - (self.end2 - self.start2)
        
        
class block_tx:
    w3 : Web3.HTTPProvider
    
    def __init__(self, w3) -> None:
         self.w3 = w3
    
    def blk_txs(self) ->list:
        return self.w3.eth.get_block(14190080).transactions
        
        