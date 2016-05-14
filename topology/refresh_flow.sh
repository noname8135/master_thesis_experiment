#/bin/bash

#usage:  bash refresh_flow.sh [switch_num]
for i in $(seq 1 $1)
do
echo s$i:
sudo ovs-ofctl dump-flows s$i
done

for i in $(seq 1 $1)
do
sudo ovs-ofctl del-flows s$i
done

