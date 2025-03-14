#!/usr/bin/env python
#
# SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import os
import requests


def get_suggestion(query: str, instructions: str, behavior: str) -> str:
    payload = json.dumps(
        {
            'integration_id': os.environ['BOT_INTEGRATION_ID'],
            'messages': [
                {'role': 'system', 'content': behavior},
                {'role': 'context'},
                {'role': 'user', 'content': instructions},
                {'role': 'query', 'content': query},
                {
                    'role': 'user',
                    'content': 'Output your response in Github markdown. Sign it as "Espressif Bot".',
                },
            ],
        }
    )

    endpoint = os.environ['BOT_API_ENDPOINT']

    if endpoint.endswith('chat/'):
        # Switch to "custom chat" feature if the URL is for simple chat
        endpoint = f'{endpoint}custom/'

    headers = {'content-type': 'application/json', 'X-API-KEY': os.environ['BOT_API_KEY']}
    r = requests.post(endpoint, data=payload, headers=headers)

    r.raise_for_status()
    j = r.json()
    try:
        answer = j['answer']
    except KeyError:
        raise RuntimeError(str(j))

    assert isinstance(answer, str), 'No answer found'

    return answer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('query_file', type=str, default=None)
    parser.add_argument('--instructions', type=str, required=True)
    parser.add_argument('--behavior', type=str, required=True)
    args = parser.parse_args()

    with (
        open(args.query_file, 'r', encoding='utf-8') as q,
        open(args.instructions, 'r', encoding='utf-8') as inst,
        open(args.behavior, 'r', encoding='utf-8') as behav,
    ):
        print(get_suggestion(q.read(), inst.read(), behav.read()))


if __name__ == '__main__':
    main()
