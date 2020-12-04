#!/bin/bash

(
cat my_command.txt | while read line
do
echo $line
sleep 2
done
)|telnet 0 20000
