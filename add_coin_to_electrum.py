import os
from dotenv import load_dotenv
from lib_logger import logger

load_dotenv()

coin = os.getenv('COIN')
rpcport = os.getenv('KMD_RPCPORT')
logger.info(f"......... coin: {coin}")

with open("/usr/local/lib/python3.8/dist-packages/electrumx/lib/coins.py", 'a') as conf:
    conf.write("\n\n")
    conf.write(f"class {coin}(KomodoMixin, EquihashMixin, Coin):\n")
    conf.write(f'    NAME = "{coin}"\n')
    conf.write(f'    SHORTNAME = "{coin.upper()}"\n')
    conf.write(f'    NET = "mainnet"\n')
    conf.write(f'    TX_COUNT = 55000\n')
    conf.write(f'    TX_COUNT_HEIGHT = 42000\n')
    conf.write(f'    TX_PER_BLOCK = 2\n')
    conf.write(f'    RPC_PORT = "{rpcport}"\n')
    conf.write(f'    PEERS = []\n')
