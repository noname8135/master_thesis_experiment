This respository contain the code for experiment of my master thesis paper.
The python files are applications for ryu controller.
In 'config/' folder, there will be different set of network environment.
------------Command--------------
topology/refresh_flow.sh will show present entry on each switch and clear them
bash refresh_flow.sh [switch_num]    make sure to add the switch num!!!

network is genrated according to .network config file,
a set of config file for a network including .port_to_switch, .entry, .link

example of a set: 
files => aaa, aaa.port_to_switch, aaa.entry, aaa.link
aaa: network description file containing switch number, link number, entry number on each switch
#aaa.link: each line contain a link a,b meaning switch a is connected to switch b
aaa.port_to_switch: get the switch each port leads to
aaa.entry: pre-install flow entry


