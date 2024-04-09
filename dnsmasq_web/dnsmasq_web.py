import asyncio
from aiohttp import web
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
            "./static/index.html",
            )

    async def get_leases(self, server_request):
        try:
            with open('host/dnsmasq.leases') as f:
                leases = f.readlines()
        except FileNotFoundError:
            leases = []
        leases = [l.split(" ") for l in leases]
        leases = [
            {
                "expires": datetime.fromtimestamp(int(parts[0])).isoformat(),
                "mac": parts[1],
                "ip": parts[2],
                "name": parts[3],
                "clientid": parts[4],
            }
            for parts in leases
        ]
        ip_addresses = [p["ip"] for p in leases]
        open_ports = await scan_ports(ip_addresses)
        for l in leases:
            l["open_ports"] = open_ports.get(l["ip"],[])
        response = json.dumps(leases, indent=2)
        return web.Response(
            text=response
        )

async def test_connect(ip, port):
    try:
        _, _ = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=1)
        return (ip, port, True)
    except (OSError, asyncio.TimeoutError):
        return (ip, port, False)


async def scan_ports(ipaddresses):
    tasks = []
    for ip in ipaddresses:
        tasks += [
            test_connect(ip, 22),
            test_connect(ip, 80),
            test_connect(ip, 443)
        ]
    result = await asyncio.gather(*tasks)
    res = {}
    for (ip, port, is_open) in result:
        if is_open:
            res[ip] = res.get(ip, [])
            res[ip].append(port)
    return res


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(name)s:%(levelname)s:%(message)s', level=loglevel)
    # os.chdir("./dnsmasq_web")
    async def main():
        try:
            logging.info(f"starting webserver at http://localhost:{port}")
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
