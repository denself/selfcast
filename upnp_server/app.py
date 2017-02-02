import asyncio

import logging
from aiohttp import web


class HttpApplication:
    port = 8888

    log = logging.getLogger(__name__)
    access_logger = logging.getLogger('aiohttp.access')

    def __init__(self, loop):
        self.loop = loop

        self.app = web.Application(loop=self.loop)

        self.handler = self.app.make_handler(access_log=self.access_logger)

        self.loop.run_until_complete(
            self.app.startup()
        )

        self.srv = self.loop.run_until_complete(
            self.loop.create_server(self.handler, '0.0.0.0', self.port)
        )

        self.init()
        self.log.info("Server started")

    def init(self):
        pass

    def stop(self):
        self.srv.close()
        self.loop.run_until_complete(self.srv.wait_closed())
        self.loop.run_until_complete(self.app.shutdown())
        self.loop.run_until_complete(self.handler.shutdown(60.0))
        self.loop.run_until_complete(self.app.cleanup())
        self.log.info("Server stopped")
