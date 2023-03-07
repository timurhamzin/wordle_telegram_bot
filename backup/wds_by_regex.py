import re
from collections import Counter
from pprint import pprint
from typing import Tuple

import requests
from bs4 import BeautifulSoup

url = "https://www.visca.com/regexdict/"

# present, missing, found = ['', set(''), '']
alphabet = 'abcdefghijklmnopqrstuvwxyz'


def process_attempts(attempts) -> Tuple[str, set, str]:
    """

    :param attempts: e.g. 'ura?tE' where `a` is present in pos other than 3,
        `E` is present in pos 5
    :return: present, missing, found, where
        present e.g. 'a2s34p5'
        missing  e.g. set('noneofthisletterswasfound')
        found e.g. 's1'
    """
    to_present, to_missing, to_found = [[], [], []]
    for attempt in attempts:
        pos = 0
        for i, symbol in enumerate(attempt, 1):
            next_symbol = ''
            if i < len(attempt):
                next_symbol = attempt[i]
            grey = symbol in alphabet
            yellow = grey and next_symbol == '?'
            grey = grey and not yellow
            green = not (grey or yellow) and (symbol in alphabet.upper())
            if any((grey, yellow, green)):
                pos += 1
            if grey:
                to_missing.append(symbol)
            elif yellow:
                to_present.append(f'{symbol}{pos}')
            elif green:
                to_found.append(f'{symbol.lower()}{pos}')
    return ''.join(to_present), set(to_missing), ''.join(to_found)


present, missing, found = process_attempts(
    [
        'Fundi?',
        'ra?the',
    ]
)

present = {m[0]: [int(d) for d in m[1]]
           for m in re.findall(r'([a-z])(\d+)', present)}
# e.g. {'a': [2], 's': [3, 4], 'p': [5]}

found = {int(m[1]): m[0]
         for m in re.findall(r'([a-z])(\d+)', found)}  # e.g. {3: 'a'}


def get_pattern():
    all = set(alphabet)
    pattern = ''
    for i in range(1, 6):
        if i in found:
            pattern = pattern + found[i]
        else:
            possible = ''.join(all - missing - set(
                char for char, pos in present.items() if i in pos))
            pattern += f'[{possible}]'
    return f'^{pattern}$'


def get_word_list(pattern):
    payload = {
        'str': f'{pattern}',
        'fstr': '',
        'ifun': 'if',
        'ccg': 'all',
        'search': 'Search'}
    files = []
    headers = {}
    response = requests.request(
        "POST", url, headers=headers, data=payload, files=files)
    soup = BeautifulSoup(response.text, features='html.parser')
    a_texts = []
    for a in soup.find_all('a'):
        if 'http://www.yourdictionary.com/' in a.attrs['href']:
            a_texts.append(a.text)
    return a_texts


def rank_words(words, chars_ranked):
    """Rank words based on char frequency.
    Words without doubles are given higher ranks"""
    ranks = {w: sum(chars_ranked.get(c, 0) for c in w) +
                1000 * (max(Counter(w).values()) == 1) for w in words}
    return sorted(ranks.items(), key=lambda i: i[1], reverse=True)


def exclude_impossible(dirty_wd_list, present_letters):
    result = []
    for wd in dirty_wd_list:
        legit = True
        for p, l in enumerate(wd, 1):
            if p in present_letters.get(l, []):
                legit = False
                break
        if legit:
            result.append(wd)
    return result


def get_helpers_for_positioning(_unknown: str, _present: dict):
    _possibles = set(''.join(_unknown) + ''.join(_present.keys()))
    _pattern = []
    for i in range(1, 6):
        _possible = _possibles - set(c for c, p in _present.items() if i in p)
        _pattern.append(f'[{"".join(_possible)}]')
    return get_word_list(f'^{"".join(_pattern)}$')


def clean_history():
    return [w.lower().replace('?', '') for w in history]


def play():
    print('possible answers: ')
    word_list = get_word_list(get_pattern())
    short_list = [w for w in word_list if not (set(present.keys()) - set(w))]
    pprint(short_list)
    print('unknown letters with ranks (frequency): ')
    unknown_ranked = {l: c for l, c in
                      sorted(Counter(''.join(short_list)).items(),
                             key=lambda kv: kv[1], reverse=True)
                      if l not in found.values() and l not in present}
    print(unknown_ranked)

    print('helper words with unknown letters: ')
    unknown_chars = ''.join(unknown_ranked.keys())
    helpers_for_unknown = get_word_list('^[' + unknown_chars + ']{5}$')
    print(rank_words(helpers_for_unknown, unknown_ranked))

    print('unoptimal helper words prioritizing unknown letters: ')
    helpers_for_unknown = get_word_list('^[' + alphabet + ']{5}$')
    print(rank_words(helpers_for_unknown, unknown_ranked)[:10], end=' ...\n')

    print()
    print('helper words for positioning known letters: ')
    ranks_for_positioning = {c: 1000 for c in present}
    ranks_for_positioning.update(unknown_ranked)
    print(rank_words(
        get_helpers_for_positioning(
            unknown_chars, present), ranks_for_positioning)[:10], end=' ...\n')


play()
# print(',\n'.join(clean_history()))
# print(len(set(clean_history())))
