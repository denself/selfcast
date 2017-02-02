import asyncio

from ssdp import SSDPServer


async def main(loop: asyncio.AbstractEventLoop):
    sock = SSDPServer.get_socket()
    await loop.create_datagram_endpoint(
        lambda: SSDPServer(loop),
        sock=sock
    )


if __name__ == '__main__':
    main_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    main_loop.run_until_complete(main(main_loop))

    try:
        main_loop.run_forever()

    except KeyboardInterrupt:
        print("Stopping server...")

    finally:
        main_loop.close()
