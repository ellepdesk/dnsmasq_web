import asyncio
from aiohttp import web
from airium import Airium
from datetime import datetime
import json
import os
import logging

port = os.environ.get('PORT', 8080)
loglevel = os.environ.get('LOGLEVEL', 'INFO')

class DnsmasqWeb:
    def __init__(self):
        self.app = web.Application()
        self.app.add_routes([web.get("/leases", self.get_leases)])
        self.app.add_routes([web.get("/", self.get_index)])
    pass


    async def get_index(self, server_request):
        return web.FileResponse(
            "static/index.html",
            )

    async def get_leases(self, server_request):
        try:
            with open('host/dnsmasq.leases') as f:
                leases = f.readlines()
        except FileNotFoundError:
            return web.Response(text="[]")
        leases = [l.split(" ") for l in leases]
        leases = [
            {
                "expires": datetime.fromtimestamp(int(parts[0])).isoformat(),
                "mac": parts[1],
                "ip": parts[2],
                "name": parts[3],
            }
            for parts in leases
            ]
        response = json.dumps(leases, indent=2)
        return web.Response(
            text=response
        )

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=loglevel)

    async def main():
        try:
            logging.info("starting webserver ...")
            dnsmasqweb = DnsmasqWeb()
            runner = web.AppRunner(dnsmasqweb.app)
            await runner.setup()
            site = web.TCPSite(runner, port=port)
            await site.start()

            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass

    asyncio.run(main())