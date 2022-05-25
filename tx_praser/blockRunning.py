import HeaderFile as hf
import AbiChecker_Origin as AO
import web3_provider

# how to convert timestamp to date: https://ethereum.stackexchange.com/questions/7287/how-to-find-the-date-of-an-ethereum-transaction-while-parsing-it-with-web3 
w3 = web3_provider.provider.w3_provider()
# block number in (2022, 2, 23, 23, 36, 21), sereval hours before Ukranie and Russian war
initialBlk : int = 14277036
Currentblk : int = w3.eth.get_block("latest")

def main():
    MPlock = hf.process.Manager().Lock()
    web3_provider.LockReceiver(MPlock)
    with hf.Prouser.ProcessPoolExecutor() as executor:
        # fuMap = executor.map(AO.starter, range(initialBlk, initialBlk+15))
        futureRes = [executor.submit(AO.starter, blknum) for blknum in range(initialBlk, initialBlk + 15)]

def singleBlk():
    MPlock = hf.process.Manager().Lock()
    web3_provider.LockReceiver(MPlock)
    AO.starter(initialBlk)
    return

if __name__ == "__main__":
    singleBlk()