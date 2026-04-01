#!/bin/bash

PATH_FILE='prod/*'

SERVER_IP='root@2.59.161.253'

PATH_IN_VM='/root/opt/training/'

scp -r $PATH_FILE $SERVER_IP:$PATH_IN_VM