#/bin/bash

#usage:  bash show_all_flow.sh [switch_num]
for i in $(seq 1 $1)
do
echo s$i:
sudo ovs-ofctl dump-flows s$i
done

