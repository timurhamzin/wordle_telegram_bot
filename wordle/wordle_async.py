import asyncio
import re
from collections import Counter
from typing import Tuple, List, Dict, Set, Optional

from utils.common import create_root_logger
from utils.common import log_exception, log, LoggingLevel
from wordle.regex_dict import RegexDictionary, create_regex_dict
from wordle.reports import unique_words_played

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


class WordleException(Exception):
    pass


class BadUserInput(WordleException):
    pass


class BadFormatting(BadUserInput):
    pass


class WordleGame:
    """Suggest next move from user attempts expressed in user notation"""

    rules = """HOW TO USE THE WORDLE BOT:

    Example of user input:

        Fundi? ra?the

    This means:
    - Two attempts were made: words 'fundi' and 'rathe'.

    - Letters in capital case designate the letters
    revealed in their correct positions.
    In this example, letter 'f' is in the 1st position in the solution.

    - Letters followed by '?' are revealed in incorrect positions.
    In the example letters 'i' and 'a' are present in the solution,
    but not in the 5th and 2nd positions, respectively.

    - All the other letters, that are in the lower case and not followed by '?',
    are missing from the solution.
    In the example, it's letters 'u', 'n', 'd', 'r', 't', 'h' and 'e'.
    """

    _displayed_words_max_count = 10

    def __init__(self, regex_dict: RegexDictionary, word_length: int):
        self._word_length = word_length
        self._attempts: List[str] = []
        self._possible_solutions: List[str] = []
        self._unknown_letters_helpers: List[Tuple[str, int]] = []
        self._mixed_letters_helpers: List[Tuple[str, int]] = []
        self._positioning_helpers: List[Tuple[str, int]] = []
        self._present: Dict[str, List[int]] = {}
        self._missing: Set[str] = set()
        self._found: Dict[int, str] = {}
        self._regex_dict = regex_dict
        self._default_word_score = 1000

    async def play(self, attempts: List[str]) -> Optional[str]:
        """Provide suggestions for the next move based on previous attempts'
        results"""

        self._check_attempts_formatting(attempts)
        self._attempts = attempts

        self._process_attempts()

        word_list = await self._regex_dict.get_word_list(
            self._get_possibles_regex_dict_pattern())
        if not word_list:
            log_exception(__name__, WordleException(
                'No words were found to match all of your attempts.'
            ))
            return None

        self._possible_solutions = [
            w for w in word_list if not (set(self._present.keys()) - set(w))]
        if not self._possible_solutions:
            log_exception(__name__, WordleException(
                'No words were found to match all of your attempts.'
            ))
            return None

        unknown_chars_ranked: Dict[str, int] = {
            l: c for l, c in
            sorted(Counter(''.join(self._possible_solutions)).items(),
                   key=lambda kv: kv[1], reverse=True)
            if l not in self._found.values() and l not in self._present}

        unknown_chars: str = ''.join(unknown_chars_ranked.keys())
        helpers_for_unknown: Optional[List[str]] = (
            await self._regex_dict.get_word_list(
                '^[' + unknown_chars + ']{' + str(self._word_length) + '}$'))
        if helpers_for_unknown:
            self._unknown_letters_helpers = self._rank_words(
                helpers_for_unknown, unknown_chars_ranked)

        helpers_mixed: Optional[List[str]] = (
            await self._regex_dict.get_word_list(
                '^[' + ALPHABET + ']{' + str(self._word_length) + '}$'))
        if helpers_mixed:
            self._mixed_letters_helpers = self._rank_words(
                helpers_mixed, unknown_chars_ranked)

        ranks_for_positioning = {
            c: self._default_word_score for c in self._present}
        ranks_for_positioning.update(unknown_chars_ranked)
        self._positioning_helpers = self._rank_words(
            await self._get_positioning_helpers(unknown_chars, self._present),
            ranks_for_positioning)

        response: str = self.generate_response()
        log(
            __name__, (
                f'Generated response.\n'
                f'User input:\n'
                f'{attempts}\n'
                f'Response:\n'
                f'{response}'
            ), LoggingLevel.INFO)

        return response

    def generate_response(self) -> str:
        response: List[str] = []
        limit: int = self._displayed_words_max_count

        response.append('Possible solutions:\n')
        response.extend(self._possible_solutions[:limit])

        response.append('\nHelper words for uncovering untried letters:\n')
        response.extend(w for w, _ in self._unknown_letters_helpers[:limit])

        response.append('\nHelper words for positioning uncovered letters:\n')
        response.extend(w for w, _ in self._positioning_helpers[:limit])

        response.append('\nRandom words of given length:\n')
        response.extend(w for w, _ in self._mixed_letters_helpers[:limit])

        return '\n'.join(response)

    def _check_attempts_formatting(self, attempts):
        """Raise value error if any attempts
        do not comply with user notation and word length."""
        abc_set = set(ALPHABET)
        if not all(len(a) == self._word_length
                   for a in unique_words_played(attempts)):
            log_exception(
                __name__, BadFormatting(
                    'Incorrectly formatted input: make sure all attempts '
                    f'contain {self._word_length} letters, excluding `?`.'
                )
            )
        for attempt in map(str.lower, attempts):
            if '??' in attempt:
                log_exception(
                    __name__, BadFormatting(
                        'Use only latin alphabet characters and `?`.'
                        'Put `?` only once after letters revealed in '
                        'incorrect positions.'
                    ))
            elif set(attempt.replace('?', '')) - abc_set:
                log_exception(
                    __name__, BadFormatting(
                        'Use only latin alphabet characters and `?`.'
                    ))

    def _get_possibles_regex_dict_pattern(self):
        """Returns regex pattern to input into the regex dictionary to
        get possible solutions from it"""
        abc = set(ALPHABET)
        pattern = ''
        for i in range(1, self._word_length + 1):
            if i in self._found:
                pattern = pattern + self._found[i]
            else:
                possible = ''.join(abc - self._missing - set(
                    char for char, pos in self._present.items() if i in pos))
                pattern += f'[{possible}]'
        return f'^{pattern}$'

    def _process_attempts(self) -> None:
        """Extracts information about which letters are guessed (found),
        missing from the solution, or present in it at unknown positions.
        Example of self._present = {'a': [2], 's': [3, 4], 'p': [5]}
        Example of self._missing = {'b', 'd'}
        Example of self._found = {3: 'a'}
        """
        present, self._missing, found = self._decode_attempts_to_str_notation()

        self._present = {m[0]: [int(d) for d in m[1]]
                         for m in re.findall(r'([a-z])(\d+)', present)}

        self._found = {int(m[1]): m[0]
                       for m in re.findall(r'([a-z])(\d+)', found)}

        return None

    def _decode_attempts_to_str_notation(self) -> Tuple[str, set, str]:
        """Decodes attempts from user notation to string-notation.

        Example of attempt (user notation): 'ura?tE' where `a` is present
            in pos other than 3, `E` is present in pos 5

        Returns (present, missing, found), where
            present e.g. 'a2s34p5'
            missing  e.g. set('noneofthisletterswasfound')
            found e.g. 's1'
        """
        to_present: List[str]
        to_missing: List[str]
        to_found: List[str]
        to_present, to_missing, to_found = [[], [], []]
        for attempt in self._attempts:
            pos: int = 0
            for i, symbol in enumerate(attempt, 1):
                next_symbol = ''
                if i < len(attempt):
                    next_symbol = attempt[i]
                grey = symbol in ALPHABET
                yellow = grey and next_symbol == '?'
                grey = grey and not yellow
                green = not (grey or yellow) and (symbol in ALPHABET.upper())
                if any((grey, yellow, green)):
                    pos += 1
                if grey:
                    to_missing.append(symbol)
                elif yellow:
                    to_present.append(f'{symbol}{pos}')
                elif green:
                    to_found.append(f'{symbol.lower()}{pos}')
        return ''.join(to_present), set(to_missing), ''.join(to_found)

    def _rank_words(self, words, chars_ranked: Dict[str, int]
                    ) -> List[Tuple[str, int]]:
        """Rank words based on letter scores given by `chars_ranked`.
        Words with duplicated letters are downgraded."""
        ranks = {
            w: sum(chars_ranked.get(c, 0) for c in w)
               + self._default_word_score * (max(Counter(w).values()) == 1)
            for w in words}
        return sorted(ranks.items(), key=lambda i: i[1], reverse=True)

    async def _get_positioning_helpers(self, _unknown: str, _present: dict):
        """Get a list of words to help player position the letters that
        are known to be present in the solution."""
        _possibles = set(''.join(_unknown) + ''.join(_present.keys()))
        _pattern = []
        for i in range(1, self._word_length + 1):
            _possible = _possibles - set(
                c for c, p in _present.items() if i in p)
            _pattern.append(f'[{"".join(_possible)}]')
        return await self._regex_dict.get_word_list(f'^{"".join(_pattern)}$')


if __name__ == '__main__':
    create_root_logger()
    my_game = WordleGame(
        regex_dict=create_regex_dict(timeout_secs=10), word_length=5
    )
    play_coro = my_game.play()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(play_coro)
    loop.close()
