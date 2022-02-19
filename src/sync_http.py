import requests
from prompt_toolkit import PromptSession
import concurrent.futures
import structlog
import logging


logger: structlog.stdlib.BoundLogger = structlog.wrap_logger(
    logging.getLogger(__name__),
    wrapper_class=structlog.stdlib.BoundLogger
)


def call_open_movie_database(input_data, id) -> dict:
    try:
        d = input_data.copy()
        d['page'] = id
        result = requests.get('http://www.omdbapi.com/', params=d)
        logger.info(f'Result finished in with status of {result.status_code}')
        return result.json()
    except:
        logger.error('Issue in api call', exc_info=True)


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
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(20):
            f = executor.submit(
                call_open_movie_database,
                input_data,
                i
            )
            futures.append(f)
        
        for future in concurrent.futures.as_completed(futures):
            logger.info(future.result())


if __name__ == '__main__':
    main()

