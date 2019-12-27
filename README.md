<h1>Flow Control in a mininet environment using a Ryu controller</h1>
This project is intended to demonstrate how does a Software Defined Network works and how easy it is to program a controller to build flows in Open vSwitches.

<h3>
  Tools
</h3>
 <ul>
  <li>
    Mininet: http://mininet.org/ (it's preferable to use the mininet vm)
  </li>
  <li>
    Ryu Controller: https://osrg.github.io/ryu/
  </li>
 </ul>

<h3>
  Implementation
</h3>

<img src="https://github.com/GansoLoko/flow-control-with-mininet-and-ryu/blob/master/enviroment.png" />

We'll be build this environment using mininet. If we send any package from h1 to h2 with the destination port 5001, it should flow through the flow 1. 5002 should pick the flow 2 and 5003 the flow 3.
The enviroment implementation is in file 'env.py', and should be run using mininet.
The controller logic implementation is in file 'ovs.py', and should be run using ryu.

<h5>Any Doubts?</h5>
Please, send me an email!
I'll answer you as soon as possible.
