![CircleCI Badge](https://img.shields.io/circleci/build/github/SSS-Says-Snek/hisock)
[![Documentation Status](https://readthedocs.org/projects/hisock/badge/?version=latest)](https://hisock.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b071d22550484b5db3ad95434f2713dd)](https://www.codacy.com/gh/SSS-Says-Snek/hisock/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=SSS-Says-Snek/hisock&amp;utm_campaign=Badge_Grade)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/SSS-Says-Snek/hisock.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/SSS-Says-Snek/hisock/context:python)
[![Downloads](https://static.pepy.tech/personalized-badge/hisock?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads)](https://pepy.tech/project/hisock)

![PyPI Version](https://img.shields.io/pypi/v/hisock)
![Github Version](https://img.shields.io/github/v/release/SSS-Says-Snek/hisock)
![Github Commits](https://img.shields.io/github/commits-since/SSS-Says-Snek/hisock/latest)

<img src="https://raw.githubusercontent.com/SSS-Says-Snek/SSS-Says-Snek.github.io/master/assets/logo.png" width=200 class="center">

# hisock (HiSock)
A ***hi***gher level extension of Python's ***sock***et module, with simpler and more efficient usages.

## Documentation
Documentation is located on 
[ReadTheDocs](https://hisock.readthedocs.io). Some documentation is also located in the code as docstrings, though most are 
already well-documented on ReadTheDocs.

## Installation
Hisock only supports Python versions 3.7 and onwards, due to annotations from the `__future__` module.

`hisock` is available on PyPI, [here](https://pypi.org/project/hisock), so it is installable by `pip`. Just do the following command.
```shell
$ python -m pip install hisock (WINDOWS)
  OR
$ pip3 install hisock (MAC/LINUX)
```

---

To build the *bleeding-edge* version of hisock from GitHub, download the repository with your favorite way, `cd` into it, then type:
```shell
$ python -m pip install -e . (WINDOWS)
  OR
$ pip3 install -e . (MAC/LINUX)
```
Note that you **MUST** cd into the cloned directory for this to work.

## Examples
hisock utilizes decorators as the core of receiving messages instead of having 
if statements handling all of the logic. 
More in-depth examples are located in the `examples` directory, including a tic-tac-toe game. Here is what a basic 
server script would look like using hisock:

#### Server
```python
import sys
import time
import random

from hisock import start_server, get_local_ip, iptup_to_str

ADDR = get_local_ip()
PORT = 6969

if len(sys.argv) == 2:
    ADDR = sys.argv[1]
if len(sys.argv) == 3:
    PORT = int(sys.argv[2])

print(f"Serving at {ADDR}")
server = start_server((ADDR, PORT))

@server.on("join")
def client_join(client_data):
    print(f"Cool, {':'.join(map(str, client_data['ip']))} joined!")
    if client_data['name'] is not None:
        print(f"    - With a sick name \"{client_data['name']}\", very cool!")
    if client_data['group'] is not None:
        print(f"    - In a sick group \"{client_data['group']}\", cool!")

    print("I'm gonna send them a quick hello message")

    server.send_client(client_data['ip'], "hello_message", str(time.time()).encode())

@server.on("processing1")
def process(client, process_request: str):
    print(f"\nAlright, looks like {iptup_to_str(client['ip'])} received the hello message, "
          "\nas now they're trying to compute something on the server, because they have "
          "potato computers")
    print("Their processing request is:", process_request)

    for _ in range(process_request.count("randnum")):
        randnum = str(random.randint(1, 100000000))
        process_request = process_request.replace("randnum", randnum, 1)

    result = eval(process_request)  # Insecure, but I'm lazy, so...
    print(f"Cool! The result is {result}! I'mma send it to the client")

    server.send_client_raw(client['ip'], str(result).encode())


while not server.closed:
    server.run()
```

#### Client
```python
import time

from hisock import connect, get_local_ip

server_to_connect = input("Enter server IP to connect to (Press enter for default of your local IP): ")
port = input("Enter Server port number (Press enter for default of 6969): ")

if server_to_connect == '':
    server_to_connect = get_local_ip()

if port == '':
    port = 6969
else:
    port = int(port)

name = input("Name? (Press enter for no name) ")
group = input("Group? (Press enter for no group) ")

print("======================================= ESTABLISHING CONNECTION =======================================")

if name == '':
    name = None
if group == '':
    group = None

join_time = time.time()

s = connect(
    (server_to_connect, port),
    name=name, group=group
)


@s.on("hello_message")
def handle_hello(msg):
    print("Thanks, server, for sending a hello, just for me!")
    print(f"Looks like, the message was sent on timestamp {msg.decode()}, "
          f"which is just {round(float(msg.decode()) - join_time, 6) * 1000} milliseconds since the connection!")
    print("In response, I'm going to send the server a request to do some processing")

    s.send("processing1", b"randnum**2")
    result = int(s.recv_raw())

    print(f"WHOAAA! The result is {result}! Thanks server!")

while not s.closed:
    s.update()

```

###### Copyright SSS-Says-Snek, 2021-present
