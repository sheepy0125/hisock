import socket
import json
import errno
import sys
import traceback

from utils import make_header, removeprefix


class HiSockClient:
    def __init__(self, addr, name, group, blocking=True, header_len=16):
        self.funcs = {}

        self.addr = addr
        self.name = name
        self.group = group
        self.header_len = header_len

        self._closed = False

        self.reserved_functions = ['client_connect']

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        self.sock.setblocking(blocking)

        hello_dict = {"name": self.name, "group": self.group}
        conn_header = make_header(f"$CLTHELLO$ {hello_dict}", self.header_len)

        self.sock.send(
            conn_header + f"$CLTHELLO$ {json.dumps(hello_dict)}".encode()
        )

    def update(self):
        if not self._closed:
            try:
                while True:
                    content_header = self.sock.recv(self.header_len)

                    if not content_header:
                        print("[SERVER] Connection forcibly closed by server, exiting...")
                        raise SystemExit
                    content = self.sock.recv(int(content_header.decode()))

                    if content.startswith(b"$CLTCONN$") and 'client_connect' in self.funcs:
                        clt_content = json.loads(
                            removeprefix(content, b"$CLTCONN$ ")
                        )
                        self.funcs['client_connect'](clt_content)

                    for matching_cmd, func in self.funcs.items():
                        if content.startswith(matching_cmd.encode()) and \
                                matching_cmd not in self.reserved_functions:
                            parse_content = content[len(matching_cmd) + 1:]
                            func(parse_content)
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK and not self._closed:
                    # Fatal Error, abort client
                    traceback.print_exception(
                        type(e), e, e.__traceback__, file=sys.stderr
                    )
                    print("\nServer Error encountered, aborting client...", file=sys.stderr)
                    self.close()

                    raise SystemExit

    class _on:
        """Decorator used to handle something when receiving command"""
        def __init__(self, outer, something):
            self.outer = outer
            self.something = something

        def __call__(self, func):
            def inner_func(*args, **kwargs):
                ret = func(*args, **kwargs)
                return ret

            self.outer.funcs[self.something] = func
            return inner_func

    def on(self, something):
        return HiSockClient._on(self, something)

    def send(self, command: str, content: bytes):
        content_header = make_header(command.encode() + b" " + content, self.header_len)
        self.sock.send(
            content_header + command.encode() + b" " + content
        )

    def raw_send(self, content):
        header = make_header(content, self.header_len)
        self.sock.send(
            header + content
        )

    def wait_recv(self):
        msg_len = int(self.sock.recv(self.header_len).decode())
        message = self.sock.recv(msg_len)
        return message

    def close(self):
        self._closed = True
        self.sock.close()


def connect(addr, name=None, group=None):
    return HiSockClient(addr, name, group)


if __name__ == "__main__":
    s = connect(('192.168.1.131', 33333), name="Sussus", group="Amogus")

    @s.on("Joe")
    def hehe(msg):
        print("Wowie", msg)
        yes = s.wait_recv()
        print(yes)
        s.send("Sussus", b"Some random msg I guess")

    @s.on("pog")
    def eee(msg):
        print("Pog juice:", msg)
        # s.close()

    @s.on("client_connect")
    def please(data):
        print("YESSSSSSSSSSS")
        print(data)

    while True:
        s.update()
