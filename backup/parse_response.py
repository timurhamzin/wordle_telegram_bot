import logging
import time
from http import HTTPStatus
from json import JSONDecodeError
from typing import Dict, Any

import requests

from check_homework_status_bot import PRACTICUM_TOKEN, API_URL


def parse_homework_status(homework: dict) -> str:
    try:
        homework_name = homework['homework_name']
        status = homework['status']
    except KeyError as e:
        logging.error(f'Error parsing homework: {e}')
        raise
    if status == 'rejected':
        verdict = 'There are issues in your homework.'
    elif status == 'approved':
        verdict = ('Your homework was accepted by the reviewer. '
                   'You can proceed with your studies.')
    else:
        verdict = ('Your homework has been assigned an unknown status. '
                   'Something must have changed in the homework API.')
        logging.error(f'Unknown homework status: {status}')
    return f'Your work was reviewed: "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp: int) -> Dict:
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        response = requests.get(url=API_URL, headers=headers, params=params)
    except requests.RequestException as e:
        logging.error(f'Error requesting the API: {e}')
        raise
    if response.status_code != HTTPStatus.OK:
        logging.warning(f'API request returned status {response.status_code}')
    try:
        return response.json()
    except JSONDecodeError as e:
        logging.error(f'Error decoding API response: {e}')
        raise


def get_current_timestamp(homework_statuses: dict) -> int:
    try:
        current_timestamp: int = int(homework_statuses['current_date'])
        assert current_timestamp > 0
    except (KeyError, TypeError) as e:
        logging.error(f'Error getting current timestamp from response: {e}')
        raise
    return current_timestamp


def get_last_homework(statuses: Dict[str, Any]) -> dict:
    try:
        homeworks: dict = statuses['homeworks']
        assert isinstance(homeworks, list), (
            f'Expected a list under the `homeworks` key, got {homeworks}'
        )
        last_homework = statuses['homeworks'][0]
    except (KeyError, IndexError, AssertionError) as e:
        logging.error(f'Error getting homework from API response: {e}')
        raise
    return last_homework