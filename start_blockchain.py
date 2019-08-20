import os
import time
import sys
import subprocess
from slickrpc import Proxy

# init params
clients_to_start = 2
ac_name = 'TESTCHAIN'

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

#TODO: load bootstrap with 128 premined blocks
#TODO: can easily import hardcoded WIF and setpubkeys if needed via RPC proxy call to use relevant addresses in tests

#start numnodes daemons, changing folder name and port
for i in range(clients_to_start):
    # all nodes should search for first "mother" node
    if i == 0:
        subprocess.call(['./komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-port=' + str(8000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-whitelist=127.0.0.1', '-daemon'])
        time.sleep(5)
    else:
        subprocess.call(['./komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-port=' + str(8000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-addnode=127.0.0.1:8000', '-whitelist=127.0.0.1', '-listen=0', '-daemon'])
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

# starting mining on second node
proxy_1.setgenerate(True, 1)

# crutch - we want two (or more) daemon processes in single image (to abstract to "blockchain" rather than "node") and dont want container to stop
while True:
    time.sleep(77777777)
