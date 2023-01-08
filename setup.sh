#!/bin/sh

this="/kAFL-Customization"
dirPath=`dirname $0`

if [ "$dirPath" != *"$this" ]; then
    echo "[-] wrong directory name. must be $this"
    exit 1
fi

execDir=`pwd`
cd $dirPath/..

if [ "$execDir" != `pwd` ]; then
    echo "[-] execute on directory: `pwd`"
    exit 2
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