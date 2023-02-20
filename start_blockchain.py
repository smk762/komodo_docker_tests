import os
import time
import sys
import subprocess
from slickrpc import Proxy
from dotenv import load_dotenv
from lib_logger import logger

load_dotenv()

clients_to_start = int(os.getenv('KMD_CLIENTS'))
rpc_port = int(os.getenv('KMD_RPCPORT'))
p2p_port = int(os.getenv('KMD_P2PPORT'))
rpcpass = os.getenv('KMD_RPCPASS')
rpcuser = os.getenv('KMD_RPCUSER')
pubkey = os.getenv('KMD_PUBKEY')
addr = os.getenv('KMD_ADDRESS')
wif = os.getenv('KMD_WIF')
ac_name = os.getenv('KMD_AC_NAME')
ac_params = os.getenv('KMD_AC_PARAMS').split(" ")

# expecting REGTEST or REGULAR there
chain_start_mode = 'REGTEST'
if 'CHAIN_MODE' in os.environ:
    chain_start_mode = os.getenv('CHAIN_MODE')

logger.info(f"clients_to_start: {clients_to_start}")
logger.info(f"rpc_port: {rpc_port}")
logger.info(f"p2p_port: {p2p_port}")
logger.info(f"rpcpass: {rpcpass}")
logger.info(f"rpcuser: {rpcuser}")
logger.info(f"pubkey: {pubkey}")
logger.info(f"ac_name: {ac_name}")
logger.info(f"ac_params: {ac_params}")
logger.info(f"ac_params: {ac_params}")

# pre-creating separate folders and configs
for i in range(clients_to_start):
    node_dir = f"/data/node_{i}"
    try:
        os.mkdir(node_dir)
        open(f"{node_dir}/{ac_name}.conf", 'a').close()
        with open(f"{node_dir}/{ac_name}.conf", 'a') as conf:
            conf.write(f"rpcuser={rpcuser}\n")
            conf.write(f"rpcpassword={rpcpass}\n")
            conf.write(f"rpcport={rpc_port + i}\n")
            conf.write("rpcbind=0.0.0.0\n")
            conf.write("rpcallowip=0.0.0.0/0\n")
    except:
        logger.info(f"{node_dir} already exists, skipping conf append.")

logger.info('config is ready')

#start numnodes daemons, changing folder name and port
for i in range(clients_to_start):
    # all nodes should search for first "mother" node
    conf_path = f"{sys.path[0]}/node_{i}/{ac_name}.conf"
    logger.info(conf_path)

    if i == 0:
        start_args = ['./komodod', '-ac_name='+ac_name, f"-conf={conf_path}", f'-rpcport={rpc_port + i}',
                         f'-port={p2p_port + i}', f'-datadir={sys.path[0]}/node_{i}', '-daemon'] + ac_params
    else:
        start_args = ['./komodod', '-ac_name='+ac_name, f"-conf={conf_path}", f'-rpcport={rpc_port + i}',
                         f'-port={p2p_port + i}', f'-datadir={sys.path[0]}/node_{i}',
                         f'-addnode=127.0.0.1:{p2p_port}', '-listen=0', f'-pubkey={pubkey}', '-daemon'] + ac_params

    if chain_start_mode == 'REGTEST':
        start_args.append('-regtest')
    subprocess.call(start_args)
    time.sleep(5)


#creating rpc proxies for all nodes
for i in range(clients_to_start):
    rpcport = rpc_port + i
    globals()[f'proxy_{i}'] = Proxy(f"http://{rpcuser}:{rpcpass}@127.0.0.1:{rpcport}")
time.sleep(2)

#checking if proxies works as expected
for i in range(clients_to_start):
    while True:
        try:
            getinfo_output = globals()['proxy_%s' % i].getinfo()
            logger.info(getinfo_output)
            break
        except Exception as e:
            logger.info(e)
            time.sleep(2)

# importing test address to public node
proxy_0.importprivkey(wif)

# starting blocks creation on second node, mining rewards will get first public node because of pubkey param
if chain_start_mode == 'REGTEST':
    while True:
        if clients_to_start > 1:
            proxy_1.generate(1)
        else:
            proxy_0.generate(1)
        time.sleep(2)
else:
    if clients_to_start > 1:
        logger.info("$$$$$$$$$$$$$$$$$$$$ Starting mining on node 2")
        proxy_1.setgenerate(True, 1)
    else:
        logger.info("$$$$$$$$$$$$$$$$$$$$ Starting mining on node 1")
        proxy_0.setgenerate(True, 1)
