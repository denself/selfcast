import asyncio
import datetime
import random
import socket
import struct
import sys
from typing import Tuple, Dict


class SSDPServer(asyncio.DatagramProtocol):
    address = '239.255.255.250'
    port = 1900
    transport: asyncio.DatagramTransport = None
    MSEARCH_HEADER = b"M-SEARCH * HTTP/1.1\r\n"

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    @classmethod
    def get_socket(cls) -> socket.socket:

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        group = socket.inet_aton(cls.address)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(('', cls.port))

        return sock

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
        # TODO send notify messages

    def datagram_received(self, data: bytes, address: Tuple[str, int]):
        if data.startswith(self.MSEARCH_HEADER):
            headers = self.parse_http_header(data)
            if headers \
                    .get('ST', '') \
                    .startswith('urn:dial-multiscreen-org:service:dial:'):
                mx = int(headers['MX'])
                delay = random.random() * mx

                asyncio.async(self.send_response(delay, address))

    async def send_response(self, delay: float, addr: Tuple[str, int]):
        await asyncio.sleep(delay)
        await self.loop.create_datagram_endpoint(ResponseSender,
                                                 remote_addr=addr)

    @staticmethod
    def parse_http_header(text: bytes) -> Dict[str, str]:

        lines = text.decode('ASCII').rstrip().split('\r\n')[1:]
        result = {}
        for line in lines:
            key, value = line.split(':', 1)
            result[key.upper()] = value.strip()
        return result


class ResponseSender(asyncio.DatagramProtocol):
    def connection_made(self, transport: asyncio.DatagramTransport):
        local_addr, port = transport.get_extra_info('sockname')
        response = self.get_response(local_addr)
        transport.sendto(response)

    @staticmethod
    def get_response(local_addr: str) -> bytes:
        now = datetime.datetime.utcnow()
        port = 8008
        name = "SelfCast"
        version = '0.0.1'
        config = 1
        service_location = f"http://{local_addr}:{port}/upnp/description.xml"
        pv = sys.version_info
        server_name = f"Python/{pv[0]}.{pv[1]} UPnP/1.1 {name}/{version}"
        service_type = "urn:dial-multiscreen-org:service:dial:1"
        response = \
            "HTTP/1.1 200 OK\r\n" + \
            "CACHE-CONTROL: max-age=1800\r\n" + \
            f"DATE: {now:%a, %d %b %Y %H:%M:%S} GMT\r\n" + \
            "EXT: \r\n" + \
            f"LOCATION: {service_location}\r\n" + \
            f"SERVER: {server_name}\r\n" + \
            f"ST: {service_type}\r\n" + \
            f"CONFIGID.UPNP.ORG: {config}\r\n\r\n"

        return response.encode('ASCII')
