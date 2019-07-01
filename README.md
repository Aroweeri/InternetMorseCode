# InternetMorseCode

Allow two computers to send morse code back and forth with minimal network usage.
Once both machines are connected, the user can use the gui's buttons as a morse code input method.

Local feedback is provided to indicate what the timing of the signal sounds like to the remote machine.

## Setup / Dependencies
Python3 Application
Python modules `pyaudio` and `keyboard` and `appjar` need to be installed. 
You can use python's package manager, pip, to install these, such as
`pip install pyaudio` and `pip install keyboard` and `pip install appjar`.

Two python scripts are used to make the connection: server.py and client.py

The machine running server.py needs to be sure that it's publicly available.
If the machine is behind a NAT setup, then the router will need port 60001 forwarded.
Change this port in the source code if needed.

## Usage

On the server-side, run `python server.py <local ip address>`. The local ip address is the private
address given to your local machine, such as 192.168.1.2.
The server will wait until a client is connected.

On the client side, run `python client.py <remote public ip address>`, where the argument is the
public ip address that the server is being hosted from. This can be the machine itself or the
internet-facing router in front of it.
The client will try and connect to the server.

If a connection is made, you will be able to begin pressing the spacebar to send signals to the
connected host. At this point, the client and server are the same in terms of functionality.

When finished, press the "q" key from either side to quit the connection gracefully.

## Known Issues

Clicking the "clicker" button very fast will sometimes crash the program.
