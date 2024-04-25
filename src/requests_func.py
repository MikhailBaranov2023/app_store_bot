import aiohttp


async def get_request(url):
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        async with session.get(url) as resp:
            status_code = resp.status
            return status_code