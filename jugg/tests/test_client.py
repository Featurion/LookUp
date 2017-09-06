import asyncio
import jugg


c = jugg.client.Client('127.0.0.1', 1492)
jugg.utils.reactive_event_loop(
    asyncio.get_event_loop(),
    c.start(), c.stop(),
    False)
