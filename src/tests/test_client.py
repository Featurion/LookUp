import asyncio
import jugg

from src import client


cl = client.LookUpClient('127.0.0.1', 1492)

jugg.utils.reactive_event_loop(
    asyncio.get_event_loop(),
    cl.start(), cl.stop(),
    run_forever = False)
