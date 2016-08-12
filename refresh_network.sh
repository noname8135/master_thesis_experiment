#usage: bash refresh_network
sudo mn -c
sudo python topo_gen.py $1
#sudo mn --custom topo_gen.py --topo myNetwork --mac --test pingall
