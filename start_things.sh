#!/bin/sh

python3 -u start_blockchain.py &
python3 -u add_coin_to_electrum.py &
sleep 120
./init
