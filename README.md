# InternetMorseCode

Allow two computers to send morse code back and forth with minimal network usage.  
Once both machines are connected, the user can use the gui's buttons as a morse code input method.

Local feedback is provided to indicate what the timing of the signal sounds like to the remote machine.

## Setup / Dependencies
InternetMorseCode requires `pyaudio`, `numpy`, `appJar`, and `keyboard` modules.  
You can install these with `pip -r install requirements.txt`

For pyaudio you may need to install package portaudio19-dev if you are on Debian/Ubuntu  
`sudo apt install portaudio19-dev`

Two python scripts are used to make the connection: server.py and client.py

The machine running server.py needs to be sure that it's publicly available.
If the machine is behind a NAT setup, then the router will need port 60001 forwarded.
Change this port in the source code if needed.

## Usage

On the server-side, run `python server.py <local ip address>`. The local ip address is the private
address given to your local machine, such as 192.168.1.2.
The server will wait until a client is connected.

On the client side, run `python client.py <remote public ip address> <username>`,
where the argument is the public ip address that the server is being hosted from.
This can be the machine itself or the internet-facing router in front of it.
The client will try and connect to the server.

If a connection is made, you will be able to send audio pulses to other clients connected to the
server by clicking the button.

When you are finished, click the exit button to close the connection.

## Known Issues

Clicking the "paddle" button very fast will sometimes crash the program.
