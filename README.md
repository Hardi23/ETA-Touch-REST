# ETA-Rest-API
Access and control your ETA Touch device over the network

This project is going to be the base for a Home-Assistant-Integration,
for which I will start the project soon.

## Usage
- Simply supply your local ip of your ETA-Touch-Device and use the interactive menu to read data coming from the sensors
- val : Print the values of the currently accessed Sensor
- back : Go up menu tree
- 'Name of Menu' : Enter the given submenu if it exists
- getEP : Directly get a sensor by supplying the bus address (like "/120/10101/0/0/12476")
- print : Dump all collected sensor data to an interactive HTML file
- exit : Exits the program
