import aiohttp
from prompt_toolkit import PromptSession
import asyncio
import structlog
import logging
import sys


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
)

logger: structlog.stdlib.AsyncBoundLogger = structlog.wrap_logger(
    logging.getLogger(__name__),
    wrapper_class=structlog.stdlib.AsyncBoundLogger
)

async def call_open_movie_database(session: aiohttp.ClientSession, input_data, id):
    try:
        d = input_data.copy()
        d['page'] = id
        async with session.get('http://www.omdbapi.com/', params=d) as rsp:
            result = await rsp.json()
            status = rsp.status
            await logger.info(f'Result finished in with status of {status}')
            return result
    except Exception:
        await logger.error('Async task failed', exc_info=True)


async def main():
    session = PromptSession()
    api_token = await session.prompt_async('Paste API token: ', is_password=True)
    movie_key_word = await session.prompt_async('Movie keyword: ', is_password=False)
    await logger.info('Beginning api calls')
    input_data = {
        'apikey': api_token,
        'type': 'movie',
        's': movie_key_word,
        'page': None
    }
    async with aiohttp.ClientSession() as session:
        pending = [call_open_movie_database(
            session,
            input_data,
            i
        ) for i in range(20)]
        aggregate = await asyncio.gather(*pending)
        for i in aggregate:
            await logger.info(i)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
