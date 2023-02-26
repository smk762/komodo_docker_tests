#!/bin/sh

python3 -u start_blockchain.py &
sleep 120
tail -f /dev/null