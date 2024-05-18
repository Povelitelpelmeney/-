import asyncio
import struct
import json
import time


class SNTPProtocol(asyncio.DatagramProtocol):
    def __init__(self, s: int = 0):
        super().__init__()
        self.t = None
        self.p = struct.Struct('!BBBBIIIQQQQ')
        self.o = 2208988800
        self.s = s

    def connection_made(self, t: asyncio.DatagramTransport):
        self.t = t

    def datagram_received(self, d: bytes, a: tuple):
        try:
            r = self.p.unpack(d)
            print(f'SNTP packet: {a}')
            self.t.sendto(self.p.pack(
                0b00100100, 1, 0, 0, 0, 0, 0, 0,
                r[10], int(time.time() + self.o + self.s) * 2**32,
                int(time.time() + self.o + self.s) * 2**32
            ), a)
        except struct.error:
            print(f'invalid SNTP packet: {a}')

async def main():
    with open('config.json') as f:
        d = json.load(f)
        h, p, s = "localhost", d['port'], d['shift']
    l = asyncio.get_event_loop()
    t, _ = await l.create_datagram_endpoint(
        lambda: SNTPProtocol(s), local_addr=(h, p))
    try:
        await asyncio.sleep(1000)
    except asyncio.CancelledError:
        print('Server was shut down')
    finally:
        t.close()

if __name__ == '__main__':
    asyncio.run(main())
    
    # w32tm /stripchart /computer:localhost /dataonly