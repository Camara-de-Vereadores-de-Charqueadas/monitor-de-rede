#!/bin/bash
# run_all.sh

touch momento_erro.txt log_ping.txt

./monitora_rede.sh &

sleep 5

sleep 30
./verifica.sh