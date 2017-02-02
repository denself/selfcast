import asyncio

import logging

from upnp_server.app import HttpApplication
from ssdp_server.app import SSDPApplication


logging.basicConfig(level=logging.DEBUG)


class Application:

    log = logging.getLogger(__name__)

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.servers = []
        self.log.info("Application initialized")

    def add_server(self, server):
        self.servers.append(
            server(self.loop)
        )
        self.log.info("Server %s added", server)

    def run(self):

        try:
            self.log.info("Application started")
            self.loop.run_forever()
        except KeyboardInterrupt:  # pragma: no cover
            self.log.info("Stopping server...")
        finally:
            self.stop()

    def stop(self):
        for server in self.servers:
            server.stop()


if __name__ == '__main__':
    app = Application()
    app.add_server(SSDPApplication)
    app.add_server(HttpApplication)
    app.run()
