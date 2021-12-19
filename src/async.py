import aiohttp
from prompt_toolkit import PromptSession
import asyncio
from loguru import logger
import sys


logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True
)


async def call_open_movie_database(session: aiohttp.ClientSession, input_data, id):
    try:
        d = input_data.copy()
        d['page'] = id
        async with session.get('http://www.omdbapi.com/', params=d) as rsp:
            result = await rsp.json()
            status = rsp.status
            logger.info(f'Result finished in with status of {status}')
            return result
    except Exception as ex:
        logger.error('Async task failed')


async def main():
    session = PromptSession()
    api_token = await session.prompt_async('Paste API token: ', is_password=True)
    movie_key_word = await session.prompt_async('Movie keyword: ', is_password=False)
    logger.info('Beginning api calls')
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
            logger.info(i)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
