from abc import abstractmethod, ABC
from typing import List, Optional

import aiohttp as aiohttp
from bs4 import BeautifulSoup

from utils import log_exception, post


def create_regex_dict(timeout_secs: int = 10):
    """RegexDictionary factory"""
    return ViscaRegexDictionary(timeout_secs=timeout_secs)


class RegexDictionary(ABC):

    def __init__(self, timeout_secs: int):
        self.timeout_secs = timeout_secs

    # noinspection PyTypeChecker
    @abstractmethod
    async def get_word_list(self, pattern) -> Optional[List[str]]:
        """Returns a list of dictionary words matching the pattern
        given by `pattern`."""
        log_exception(__name__, NotImplementedError())
        return None


class ViscaRegexDictionary(RegexDictionary):

    def __init__(self, timeout_secs: int):
        super().__init__(timeout_secs)
        self._url = "https://www.visca.com/regexdict/"

    async def get_word_list(self, pattern) -> Optional[List[str]]:
        """Returns a list of dictionary words matching the pattern
        given by `pattern`."""
        async with aiohttp.ClientSession() as session:
            data = {
                'str': f'{pattern}',
                'fstr': '',
                'ifun': 'if',
                'ccg': 'all',
                'search': 'Search'}
            try:
                html = await post(
                    session, self._url, data=data,
                    timeout=self.timeout_secs, ssl=False)
            except Exception as e:
                log_exception(__name__, e)
            else:
                soup = BeautifulSoup(html, features='html.parser')
                a_texts = []
                for a in soup.find_all('a'):
                    if 'http://www.yourdictionary.com/' in a.attrs['href']:
                        a_texts.append(a.text)
                return a_texts
            return None
