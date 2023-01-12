#!/bin/bash

dirPath=`dirname $0`
execDir=`pwd`
cd $dirPath/..

if [ "$execDir" != `pwd` ]; then
    echo "[-] Execute on directory: `pwd`"
    exit 1
fi

this="kAFL-Customization"
if [[ "$dirPath" != *$this ]]; then
    echo "[-] Wrong directory name. Must be $this"
    exit 2
fi

if [ -f "./kAFL-Fuzzer/kafl.ini" ]; then
    cp ./kAFL-Fuzzer/kafl.ini ./kAFL-Customization/kafl.ini
    echo "[+] Copied kafl.ini"
fi

if [ ! -z $1 ]; then
    if [ -d "./kAFL-Fuzzer" ]; then
        if [ ! -d $1 ]; then
            mv ./kAFL-Fuzzer $1
            echo "[+] Made a backup. ($1)"
        else
            echo "[-] File already exist. Stop..."
            exit 3
        fi
    else
        echo "[-] No file to backup"
    fi
else
    if [ -d "./kAFL-Fuzzer" ]; then
        rm -rf ./kAFL-Fuzzer
    fi
fi

cp -rf ./kAFL-Customization ./kAFL-Fuzzer
if [ -f "./kAFL-Fuzzer/setup.bash" ]; then
    rm ./kAFL-Fuzzer/setup.bash
fi
echo "[*] Done"