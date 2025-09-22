#!/bin/bash
# verifica.sh

while true; do
    if [ -f "log_ping.txt" ]; then
        python3 verificarede.py
        sleep 60
    else
        sleep 10
    fi
done