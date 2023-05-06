#!/usr/bin/env python3

import io
import os
import re
import requests
import sys

default_target_name = 'default'
alias_protocol = 'alias:'

def get_targets(url_string):
    targets = {}
    if url_string:
        named_urls = url_string.split(';')
        for named_url in named_urls:
            named_url_structure = named_url.split('=')
            if len(named_url_structure) == 2:
                name = named_url_structure[0].lower()
                url_or_alias = named_url_structure[1]
                if len(name) == 0:
                    print(f'warning: empty name: "{named_url}"', file=sys.stderr)
                elif len(url_or_alias) == 0:
                    print(f'warning: empty url: "{named_url}"', file=sys.stderr)
                else:
                    if ':' in url_or_alias:
                        targets.update({ name: url_or_alias })
                    else:
                        targets.update({ name: f'{alias_protocol}{url_or_alias}'})
            elif len(named_url_structure) == 1:
                url_or_alias = named_url_structure[0]
                if len(url_or_alias) == 0:
                    print(f'warning: empty url: "{named_url}"', file=sys.stderr)
                elif default_target_name not in targets:
                    if ':' in url_or_alias:
                        targets.update({ default_target_name: url_or_alias })
                    else:
                        targets.update({ default_target_name: f'{alias_protocol}{url_or_alias}' })
                else:
                    print(f'warning: Default target is already defined: "{named_url}"', file=sys.stderr)
            else:
                print(f'warning: Invalid url format: "{named_url}"', file=sys.stderr)

    return targets

def send():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

    url_or_alias = os.environ.get('TEAMS_WEBHOOK')
    targets = get_targets(url_or_alias)
    if default_target_name in targets:
        default_url = targets[default_target_name]
    else:
        default_url = None

    import argparse
    parser = argparse.ArgumentParser(description='Send message from /dev/stdin to Microsoft Teams\' incoming webhook')
    parser.add_argument('-t', '--text', nargs=1, help=f'message instead of /dev/stdin')
    parser.add_argument('-u', '--url', nargs=1, help=f'webhook url (default: {default_url})')
    parser.add_argument('-n', '--name', nargs=1, help=f'webhook target name')
    parser.add_argument('--list', action='store_true', help='list target names')
    parser.add_argument('--dry', action='store_true', help='dry run')

    args = parser.parse_args()

    if args.url:
        url_or_alias = args.url[0]
        targets = get_targets(url_or_alias)

    if not url_or_alias:
        print('No webhook url ($TEAMS_WEBHOOK or -u parameter is necessary)', file=sys.stderr)
        return 1

    if args.list:
        for name in targets.keys():
            print(f'{name}: {targets[name]}')
        return 1

    if args.name:
        name = args.name[0].lower()
    else:
        name = default_target_name

    if name in targets.keys():
        url_or_alias = targets[name]
        while url_or_alias.startswith(alias_protocol):
            if not url_or_alias[len(alias_protocol):] in targets.keys():
                print(f'No such a webhook target name: {url_or_alias}', file=sys.stderr)
                return 1
            url_or_alias = targets[url_or_alias[len(alias_protocol):]]
        url = url_or_alias
    else:
        if name == default_target_name:
            print('Default webhook target name is not defined', file=sys.stderr)
        else:
            print(f'No such a webhook target name: {name}', file=sys.stderr)
        return 1

    if args.text:
        text = args.text[0]
    else:
        text = sys.stdin.read()

    first_line_matched = re.match(r'^(#[^\n\r]*)(\n|\r)', text)
    if first_line_matched:
        title = first_line_matched.group(1)
        text = text[first_line_matched.end():]
    else:
        title = ''

    text = re.sub(r'[\n\r]', r'  \n', text)

    message = {
        'type': 'message',
        'attachments': [
            {
                'contentType': 'application/vnd.microsoft.teams.card.o365connector',
                'content': {
                    '@type': 'MessageCard',
                    '@context': 'https://schema.org/extensions',
                    'title': title,
                    'sections': [
                        {
                            'text': text
                        }
                    ]
                }
            }
        ]
    }

    if args.dry:
        import json
        print(f'url={url_or_alias}')
        print(json.dumps(message, indent=2, ensure_ascii=False))
        return 0

    res = None
    try:
        res = requests.post(url_or_alias, json=message)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    if res:
        status = res.status_code
    else:
        status = None

    print(f'{status}')

    if status is None or status >= 400:
        return 1
    else:
        return 0

if __name__ == '__main__':
    exit(send())