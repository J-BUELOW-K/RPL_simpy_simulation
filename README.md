# RPL SimPy Simulator

## Overview
The RPL SimPy Simulator is a powerful tool designed to simulate the behavior of RPL (Routing Protocol for Low-Power and Lossy Networks) in network environments. It generates networks, displays them, and creates DIOs (DODAG Information Objects) and DAOs (Destination Advertisement Objects) to facilitate DODAG (Destination Oriented Directed Acyclic Graph) creation.

## Features
- **Network Generation**: The simulator can generate a variety of network topologies to test the performance of RPL under different conditions.
- **Network Display**: Visualize the generated networks to better understand their structure and the path of data flow.
- **DIO and DAO Creation**: The simulator creates DIOs and DAOs, essential components in RPL for the creation and maintenance of DODAGs.

## Getting Started

1. **Installation**: 
   - Clone the repository to your local machine using `git clone https://github.com/yourusername/RPL-SimPy-Simulator.git`.
   - Navigate to the cloned repository using `cd RPL-SimPy-Simulator`.

2. **Usage**: 
   - To generate a network, use the `Network` class and call `generate_nodes_and_edges(NUMBER_OF_NODES, RADIUS)`
   - To visualize the generated network, use the `plot_network` function. This will display the network with nodes and edges.
   - To create DIOs and DAOs, use the `construct_new_dodag()` function.
   - To visualize the DODAG, use the `plot_network_and_dodag` function. This will display the DODAG with nodes and edges.


## Contributing
We welcome contributions from the community.

## License
MIT License

Copyright (c) 2024 Johan Bülow Kviesgaard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Contact
For any queries or support, please contact us at email support.

## Acknowledgements
Thank you to Galfy1 and alroe19 for their contributions. 
