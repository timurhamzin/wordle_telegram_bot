from abc import abstractmethod, ABC
from typing import List

import aiohttp as aiohttp
from bs4 import BeautifulSoup

from utils import fetch, raise_with_log


def create_regex_dict(timeout_secs: int = 10):
    """RegexDictionary factory"""
    return ViscaRegexDictionary(timeout_secs=timeout_secs)


class RegexDictionary(ABC):

    def __init__(self, timeout_secs: int):
        self.timeout_secs = timeout_secs

    # noinspection PyTypeChecker
    @abstractmethod
    async def get_word_list(self, pattern) -> List[str]:
        raise_with_log(__name__, NotImplementedError())


class ViscaRegexDictionary(RegexDictionary):

    def __init__(self, timeout_secs: int):
        super().__init__(timeout_secs)
        self._url = "https://www.visca.com/regexdict/"

    async def get_word_list(self, pattern) -> List[str]:
        """Returns a list of dictionary words matching the pattern
        given by `pattern`."""
        async with aiohttp.ClientSession() as session:
            payload = {
                'str': f'{pattern}',
                'fstr': '',
                'ifun': 'if',
                'ccg': 'all',
                'search': 'Search'}
            headers = {}
            try:
                html = await fetch(
                    session, self._url, timeout=self.timeout_secs, ssl=False)
            except Exception as e:
                raise_with_log(__name__, e)
            soup = BeautifulSoup(html, features='html.parser')
            a_texts = []
            for a in soup.find_all('a'):
                if 'http://www.yourdictionary.com/' in a.attrs['href']:
                    a_texts.append(a.text)
        return a_texts
