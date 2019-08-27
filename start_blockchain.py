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
ac_name = os.environ['CHAIN']
test_address = os.environ['TEST_ADDY']
test_wif = os.environ['TEST_WIF']
test_pubkey = os.environ['TEST_PUBKEY']

# pre-creating separate folders and configs
for i in range(clients_to_start):
    os.mkdir("node_" + str(i))
    open("node_" + str(i) + "/" + ac_name + ".conf", 'a').close()
    with open("node_" + str(i) + "/" + ac_name + ".conf", 'a') as conf:
        conf.write("rpcuser=test" + '\n')
        conf.write("rpcpassword=test" + '\n')
        conf.write("rpcport=" + str(7000 + i) + '\n')
        conf.write("rpcbind=0.0.0.0\n")
        conf.write("rpcallowip=0.0.0.0/0\n")

#start numnodes daemons, changing folder name and port
for i in range(clients_to_start):
    # all nodes should search for first "mother" node
    if i == 0:
        subprocess.call(['./komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-port=' + str(8000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-whitelist=127.0.0.1', '-regtest', '-daemon'])
        time.sleep(5)
    else:
        subprocess.call(['./komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-port=' + str(8000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-addnode=127.0.0.1:8000', '-whitelist=127.0.0.1', '-regtest', '-listen=0', '-pubkey='+test_pubkey, '-daemon'])
        time.sleep(5)

#creating rpc proxies for all nodes
for i in range(clients_to_start):
    rpcport = 7000 + i
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
while True:
   proxy_1.generate(1)
   time.sleep(5)
