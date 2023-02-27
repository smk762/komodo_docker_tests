import os
import time
import sys
import subprocess
from slickrpc import Proxy
from dotenv import load_dotenv
from lib_logger import logger

load_dotenv()

clients_to_start = 2
rpc_port = int(os.getenv('KMD_RPCPORT'))
p2p_port = int(os.getenv('KMD_P2PPORT'))
rpcpass = os.getenv('KMD_RPCPASS')
rpcuser = os.getenv('KMD_RPCUSER')
pubkey = os.getenv('KMD_PUBKEY')
addr = os.getenv('KMD_ADDRESS')
wif = os.getenv('KMD_WIF')
ac_name = os.getenv('KMD_AC_NAME')
ac_params = os.getenv('KMD_AC_PARAMS').split(" ")
zmqport = rpc_port + 2

# expecting REGTEST or REGULAR there
chain_start_mode = 'REGTEST'
if 'CHAIN_MODE' in os.environ:
    chain_start_mode = os.getenv('CHAIN_MODE')

logger.info(f"ac_params: {ac_params}")

# pre-creating separate folders and configs
for i in range(clients_to_start):
    node_dir = f"/data/node_{i}"
    try:
        os.mkdir(node_dir)
    except:
        logger.info(f"{node_dir} already exists, skipping conf append.")

    with open(f"{node_dir}/{ac_name}.conf", 'w+') as conf:
        conf.write(f"rpcuser={rpcuser}\n")
        conf.write(f"rpcpassword={rpcpass}\n")
        conf.write(f"rpcport={rpc_port + i}\n")
        conf.write(f"port={p2p_port + i}\n")
        conf.write("rpcbind=0.0.0.0\n")
        conf.write("rpcallowip=0.0.0.0/0\n")
        conf.write(f"zmqpubrawtx=tcp://127.0.0.1:{zmqport + i}\n")
        conf.write(f"zmqpubhashblock=tcp://127.0.0.1:{zmqport + i}\n")
        conf.write(f"server=1\n")
        conf.write(f"txindex=1\n")
        conf.write(f"addressindex=1\n")
        conf.write(f"timestampindex=1\n")
        conf.write(f"spentindex=1\n")
        conf.write(f"uacomment=bitcore\n")
        conf.write(f"showmetrics=0\n")
        conf.write(f"rpcworkqueue=256\n")
        conf.write(f"datadir={node_dir}\n")
        conf.write("[test]\n")
        conf.write(f"rpcport={rpc_port + i}\n")
    with open(f"{node_dir}/{ac_name}.conf", 'r') as conf:
        lines = conf.readlines()
        print("contents of conf:")
        for line in lines:
            print(line)

logger.info('config is ready')

#start numnodes daemons, changing folder name and port
for i in range(clients_to_start):
    node_dir = f"/data/node_{i}"
    # all nodes should search for first "mother" node
    conf_path = f"{node_dir}/{ac_name}.conf"
    logger.info(f"conf_path: {conf_path}")

    if i == 0:
        start_args = ['./komodod', '-ac_name='+ac_name, f'-port={p2p_port + i}', f'-rpcport={rpc_port + i}', f"-datadir={node_dir}", f"-conf={conf_path}", '-daemon'] + ac_params
    else:
        start_args = ['./komodod', '-ac_name='+ac_name, f'-port={p2p_port + i}', f'-rpcport={rpc_port + i}', f"-datadir={node_dir}", f"-conf={conf_path}", f'-addnode=127.0.0.1:{p2p_port}',
                    '-listen=0', f'-pubkey={pubkey}', '-daemon'] + ac_params
    if chain_start_mode == 'REGTEST':
        start_args.append('-regtest')
    print(start_args)
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
