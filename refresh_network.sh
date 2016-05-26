#usage: bash refresh_network
sudo mn -c
rm proactive_flow_entry.txt -f
sudo python topo_gen.py 
#sudo mn --custom topo_gen.py --topo myNetwork --mac --test pingall
