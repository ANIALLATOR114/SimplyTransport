#!/bin/bash

# This script pulls the latest version of the code from the git repository and tells supervisor to reboot the process

restart_supervisor() {
    echo "Restarting Supervisor..."
    supervisorctl restart simplytransport
}

trap restart_supervisor EXIT

cd /home/niall/SimplyTransport
git pull