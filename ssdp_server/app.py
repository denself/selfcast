import logging

from ssdp_server.protocol import SSDPServerProtocol


class SSDPApplication:

    log = logging.getLogger(__name__)

    def __init__(self, loop):
        self.loop = loop
        connect = self.loop.create_datagram_endpoint(
            lambda: SSDPServerProtocol(loop),
            sock=SSDPServerProtocol.get_socket()
        )
        self.transport, protocol = self.loop.run_until_complete(connect)
        self.log.info("Server started")

    def stop(self):
        self.transport.close()
        self.log.info("Server stopped")
