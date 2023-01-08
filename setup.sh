#!/bin/sh

dirPath=`dirname $0`
execDir=`pwd`
cd $dirPath/..

if [ "$execDir" != `pwd` ]; then
    exit 0
fi

if [ -f "./kAFL-Fuzzer/kafl.ini" ]; then
    cp ./kAFL-Fuzzer/kafl.ini ./kAFL-Customization/kafl.ini
    echo "[+] Copied kafl.ini"
fi

if [ -d "./kAFL-Fuzzer" ]; then
    for (( i=0 ; ; i++ )); do
        backupFile="./Backup$i"
        if [ ! -d $backupFile ]; then
            mv ./kAFL-Fuzzer $backupFile
            echo "[+] Made a backup. ($backupFile)"
            break
        fi
    done
fi

cp -rf ./kAFL-Customization ./kAFL-Fuzzer
rm ./kAFL-Fuzzer/setup.sh
echo "[*] Done"