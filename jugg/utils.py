import asyncio
import re

from . import constants


def reactive_event_loop(loop, start, stop, run_forever):
    try:
        loop.run_until_complete(start)
        if run_forever:
            loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for task in asyncio.Task.all_tasks():
            task.cancel()

        loop.run_until_complete(stop)
        loop.stop()
        loop.close()


def validate_name(name):
    return bool(re.fullmatch(constants.NAME_REGEX, name))


__all__ = [
    reactive_event_loop,
    validate_name,
]
