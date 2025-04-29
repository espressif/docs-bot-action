#!/usr/bin/env python
#
# SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import os
import re
import requests

"""
There is a hard bot query limit of 15000 characters. Above this the query will be rejected by the server. It is not
possible to increase it or work around the limit. The following limit is smaller in order to account for the JSON
request overhead.
"""
QUERY_LIMIT = 14000


def get_suggestion(issue_body: str) -> str:
    payload = json.dumps({'integration_id': os.environ['BOT_INTEGRATION_ID'], 'query': issue_body})

    headers = {'content-type': 'application/json', 'X-API-KEY': os.environ['BOT_API_KEY']}
    r = requests.post(os.environ['BOT_API_ENDPOINT'], data=payload, headers=headers)

    r.raise_for_status()
    j = r.json()
    try:
        answer = j['answer']
    except KeyError:
        raise RuntimeError(str(j))

    assert isinstance(answer, str), 'No answer found'

    return answer


def shorten_backtick_blocks(text: str) -> str:
    """
    Iterate through the text and find all the triple backtick blocks ```.
    For each block, keep the first and the last couple of characters and add [redacted] in between.
    """

    CHAR_BLOCK = 200  # number of characters to keep at the beginning and at the end of the block
    backtick_block_re = re.compile(r'```.+?```', re.DOTALL)  # non-greedy search will not go over the block boundary

    """
    The text cannot be modified on the fly because indexes to the original search will change. Indexes will be stored in
    idx, a simple list, for example:
    [startA, endA, startB, endB] - where blocks between startA and endA, and startB and endB should be removed.
    If we add 0 to the beginning and "length" to the end of the list, and iterate through the list then we will get
    blocks which will need to be kept.
    [0, startA, endA, startB, endB, length] - which means that the following blocks should be kept:
                                                    - between 0 and startA,
                                                    - between endA and startB,
                                                    - between endB and length.
    """
    idx = [0]
    for m in re.finditer(backtick_block_re, text):
        start = m.start()
        end = m.end()
        length = end - start

        if length > 2 * CHAR_BLOCK:  # 2 is for accounting for the offset at the beginning and the end
            idx += [start + CHAR_BLOCK, end - CHAR_BLOCK]

    idx += [len(text)]

    blocks_to_keep = []
    idx_iter = iter(idx)
    for start, end in zip(idx_iter, idx_iter):  # (A, B), (C, D), (E, F) from [A, B, C, D, E, F]
        blocks_to_keep += [text[start:end]]

    return '\n[redacted]\n'.join(blocks_to_keep)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, default=None)
    args = parser.parse_args()

    text_reducing_heuristics = (shorten_backtick_blocks,)

    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
            if len(input_text) > QUERY_LIMIT:
                for heuristic in text_reducing_heuristics:
                    input_text = heuristic(input_text)
            print(get_suggestion(input_text))


if __name__ == '__main__':
    main()
