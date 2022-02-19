import time
from prompt_toolkit import PromptSession
import asyncio
import pandas as pd
import aiohttp
import structlog

import concurrent.futures
import sync_http
import async_http

structlog.configure(wrapper_class=structlog.stdlib.BoundLogger)
logger: structlog.stdlib.BoundLogger = structlog.get_logger()

_NUMBER_OF_PAGES = 20
_NUMBER_OF_ITERATIONS = 20


def run_sync_code(input_data: dict):
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(_NUMBER_OF_PAGES):
            f = executor.submit(
                sync_http.call_open_movie_database,
                input_data,
                i
            )
            futures.append(f)
        
        result = []
        for future in concurrent.futures.as_completed(futures):
            result.append(future.result())

    end = time.time()
    return ('SYNC', start, end)


async def run_async_code(input_data: dict):
    start = time.time()
    async with aiohttp.ClientSession() as session:
        pending = []
        for i in range(_NUMBER_OF_PAGES):
            p = async_http.call_open_movie_database(
                session,
                input_data,
                i
            )
            pending.append(p)

        aggregate = await asyncio.gather(*pending)
    end = time.time()
    return ('ASYNC', start, end)


def main():
    session = PromptSession()
    api_token = session.prompt('Paste API token: ', is_password=True)
    movie_key_word = session.prompt('Movie keyword: ', is_password=False)

    input_data = {
        'apikey': api_token,
        'type': 'movie',
        's': movie_key_word,
        'page': None
    }
    
    data = []
    for s in range(_NUMBER_OF_ITERATIONS):
        data.append(run_sync_code(input_data))

    loop = asyncio.get_event_loop()
    for s in range(_NUMBER_OF_ITERATIONS):
        res = loop.run_until_complete(run_async_code(input_data))
        data.append(res)
    
    df = pd.DataFrame(
        data,
        columns=['runtime', 'start', 'finish']
    )

    df['total_time'] = df['finish'] - df['start']

    mean_run_time = df[['total_time', 'runtime']].groupby(['runtime']).mean()
    logger.info(mean_run_time)


if __name__ == '__main__':
    main()
