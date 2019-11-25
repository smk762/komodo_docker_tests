import os
import time
import sys
import subprocess
from slickrpc import Proxy

# init params
#clients_to_start = 2
#ac_name = 'TESTCHAIN'
#test_address = 'R9imXLs1hEcU9KbFDQq2hJEEJ1P5UoekaF'
#test_wif = 'UqqW7f766rADem9heD8vSBvvrdfJb3zg5r8du9rJxPtccjWf7RG9'
#test_pubkey = '021607076d7a2cb148d542fb9644c04ffc22d2cca752f80755a0402a24c567b17a'

clients_to_start = int(os.environ['CLIENTS'])
rpc_port = 7000
if 'COIN_RPC_PORT' in os.environ:
    rpc_port = int(os.environ['COIN_RPC_PORT'])
ac_name = os.environ['CHAIN']
test_address = os.environ['TEST_ADDY']
test_wif = os.environ['TEST_WIF']
test_pubkey = os.environ['TEST_PUBKEY']
# expecting REGTEST or REGULAR there
chain_start_mode = 'REGTEST'
if 'CHAIN_MODE' in os.environ:
    chain_start_mode = os.environ['CHAIN_MODE']

# pre-creating separate folders and configs
for i in range(clients_to_start):
    os.mkdir("/data/node_" + str(i))
    open("/data/node_" + str(i) + "/" + ac_name + ".conf", 'a').close()
    with open("/data/node_" + str(i) + "/" + ac_name + ".conf", 'a') as conf:
        conf.write("rpcuser=test" + '\n')
        conf.write("rpcpassword=test" + '\n')
        conf.write("rpcport=" + str(rpc_port + i) + '\n')
        conf.write("rpcbind=0.0.0.0\n")
        conf.write("rpcallowip=0.0.0.0/0\n")

print('config is ready')

#start numnodes daemons, changing folder name and port
for i in range(clients_to_start):
    # all nodes should search for first "mother" node
    if i == 0:
        start_args = ['./komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(rpc_port + i), '-port=' + str(6000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-ac_sapling=1', '-whitelist=127.0.0.1']
        if chain_start_mode == 'REGTEST':
            start_args.append('-regtest')
            start_args.append('-daemon')
        else:
            start_args.append('-daemon')
        subprocess.call(start_args)
        time.sleep(5)
    else:
        start_args = ['./komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(rpc_port + i), '-port=' + str(6000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-ac_sapling=1', '-addnode=127.0.0.1:6000', '-whitelist=127.0.0.1', '-listen=0', '-pubkey='+test_pubkey]
        if chain_start_mode == 'REGTEST':
            start_args.append('-regtest')
            start_args.append('-daemon')
        else:
            start_args.append('-daemon')
        subprocess.call(start_args)
        subprocess.call(start_args)
        time.sleep(5)

#creating rpc proxies for all nodes
for i in range(clients_to_start):
    rpcport = rpc_port + i
    globals()['proxy_%s' % i] = Proxy("http://%s:%s@127.0.0.1:%d"%("test", "test", int(rpcport)))
time.sleep(2)

#checking if proxies works as expected
for i in range(clients_to_start):
    while True:
        try:
           getinfo_output = globals()['proxy_%s' % i].getinfo()
           print(getinfo_output)
           break
        except Exception as e:
           print(e)
           time.sleep(2)

# importing test address to public node
proxy_0.importprivkey(test_wif)

# starting blocks creation on second node, mining rewards will get first public node because of pubkey param
if chain_start_mode == 'REGTEST':
    while True:
       if int(os.environ['CLIENTS']) > 1:
           proxy_1.generate(1)
           time.sleep(2)
       else:
           proxy_0.generate(1)
           time.sleep(2)
else:
    if int(os.environ['CLIENTS']) > 1:
        print("Starting mining on node 2")
        proxy_1.setgenerate(True, 1)
    else:
        print("Starting mining on node 1")
        proxy_0.setgenerate(True, 1)
