import asyncio
import time
from collections import deque


class RequestLimiter:
    MAX_REQUESTS_PER_PERIOD = 60
    PERIOD = 60
    REQUEST_QUEUE = deque(maxlen=MAX_REQUESTS_PER_PERIOD)

    @staticmethod
    async def check_availability():
        # This method controls the access to the resource based in the params
        # Checks every 0.5s if the maximum number of requests is already used, if it is suspended and checks again until the period passes
        while len(RequestLimiter.REQUEST_QUEUE) == RequestLimiter.MAX_REQUESTS_PER_PERIOD and time.time() - RequestLimiter.REQUEST_QUEUE[0] < RequestLimiter.PERIOD:
            await asyncio.sleep(0.5)

        print(len(RequestLimiter.REQUEST_QUEUE))
        # When the period passes (or not yet full) add a new request to the queue
        RequestLimiter.REQUEST_QUEUE.append(time.time())

    @staticmethod
    async def call_external_api(fn, *args, **kwargs):
        try:
            # Before execute the function check if the process have a free slot
            # Uses await so maintains the loop free to other actions
            await RequestLimiter.check_availability()
            return await fn(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Some error occur during execution: {str(e)}")
