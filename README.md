This respository contain the code for experiment of my master thesis paper.
The python files are applications for ryu controller.
In 'config/' folder, there will be different set of network environment.
We write the topology type in topo_gen.py, and the corresponding config file will be generated if it doens't exist.
## Config files example ##
A set of config file for a network AAA including AAA, AAA.port_to_switch, AAA.entry

* AAA: network description file containing switch number, entry number of a switch, total entry number
* AAA.port_to_switch: get the switch each port leads to
* AAA.entry: pre-install flow entry details



## Commands ##
### Experiment running steps ###
1. startx: start x-window for experiment with multiple windows
1. Edit topology type, number of entries on each switch in topo_gen.py
1. bash refresh_network.sh: refresh network and start mininet
1. sudo ryu-manage flow_entry_verification.py: Start the controller and run experiment, results including aggregation rates, execution times, number of auxiliary entries etc will be shown.  
                                                         
### Others ###
bash refresh_flow.sh [switch_num]: Show present entry on each switch and clear them. Make sure to add the switch num

## Figures ##
* All figures(including their editable files) can be found in figures/.
* Figure 1 is the flowchart of detection process.
* Figure 2~4 are all experimental results, they are generated from the correspondent *.csv (also in figures/) with power point.

### figure and editable file ###
Figure   | Value
-------- | ---
1        | flow_entry_detection_flowchart.xml (Using draw IO: https://www.draw.io/)
2~4      | fig_for_exp.pptx (Export to PDF one by one)
