#!/usr/bin/env python3

import io
import os
import re
import requests
import sys

default_target_name = 'default'
alias_protocol = 'alias:'
message_types = {'msg', 'message', 'm'}
card_types = {'card', 'c'}

def parse_url_entry(value):
    """Parse 'type:url' or plain url. Returns (url, is_message)."""
    m = re.match(r'^(msg|message|m|card|c):(https?://.+)$', value, re.IGNORECASE)
    if m:
        type_prefix = m.group(1).lower()
        url = m.group(2)
        return url, type_prefix in message_types
    return value, False  # default: card

def get_targets(url_string):
    targets = {}
    if url_string:
        named_urls = url_string.split(';')
        for named_url in named_urls:
            named_url_structure = named_url.split('=', 1)
            if len(named_url_structure) == 2:
                name = named_url_structure[0].lower()
                value = named_url_structure[1]
                if len(name) == 0:
                    print(f'warning: empty name: "{named_url}"', file=sys.stderr)
                elif len(value) == 0:
                    print(f'warning: empty url: "{named_url}"', file=sys.stderr)
                else:
                    if re.match(r'^https?://', value) or re.match(r'^(msg|message|m|card|c):', value, re.IGNORECASE):
                        targets[name] = value
                    else:
                        alias = value.lower()
                        targets[name] = f'{alias_protocol}{alias}'
            elif len(named_url_structure) == 1:
                value = named_url_structure[0]
                if len(value) == 0:
                    print(f'warning: empty url: "{named_url}"', file=sys.stderr)
                elif default_target_name not in targets:
                    if re.match(r'^https?://', value) or re.match(r'^(msg|message|m|card|c):', value, re.IGNORECASE):
                        targets[default_target_name] = value
                    else:
                        alias = value.lower()
                        targets[default_target_name] = f'{alias_protocol}{alias}'
                else:
                    print(f'warning: Default target is already defined: "{named_url}"', file=sys.stderr)
            else:
                print(f'warning: Invalid url format: "{named_url}"', file=sys.stderr)

    return targets

def markdown(text):
    converted = ''
    last = 0
    matches = re.finditer(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', text)
    for m in matches:
        link = m.group()
        start = m.start()
        end = start + len(m.group())
        if last < start:
            converted = converted + text[last:start]
        converted = converted + f'[{link}]({link})'
        last = end
    if last < len(text):
        converted = converted + text[last:len(text)]
    return converted

def build_card_message(text):
    md = markdown(text)
    md = re.sub(r'[\n\r]', r'  \n', md)
    return {
        'text': text,
        'attachments': [
            {
                'contentType': 'application/vnd.microsoft.card.adaptive',
                'content': {
                    '$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
                    'type': 'AdaptiveCard',
                    'version': '1.4',
                    'padding': 'none',
                    'body': [
                        {
                            'type': 'TextBlock',
                            'text': md,
                            'wrap': True
                        }
                    ]
                }
            }
        ]
    }

def anchorize(text):
    converted = ''
    last = 0
    for m in re.finditer(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', text):
        start, end = m.start(), m.end()
        if last < start:
            converted += text[last:start]
        link = m.group()
        converted += f'<a href="{link}">{link}</a>'
        last = end
    converted += text[last:]
    return converted

def build_message_message(text):
    html = anchorize(text).replace('\n', '<br>')
    return {
        'text': html
    }

def send():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

    import argparse
    parser = argparse.ArgumentParser(description='Send message from /dev/stdin to Microsoft Teams\' incoming webhook')
    parser.add_argument('-n', '--name', nargs=1, default=None, help=f'webhook target name')
    parser.add_argument('-u', '--url', nargs=1, default=None, help=f'webhook url')
    parser.add_argument('--list', action='store_true', help='list target names')
    parser.add_argument('--dry', action='store_true', help='dry run')

    args = parser.parse_args()

    if args.name:
        name = args.name[0].lower()
    else:
        name = default_target_name

    url_or_alias = os.environ.get('TEAMS_WEBHOOK')
    targets = get_targets(url_or_alias)

    if args.list:
        for name in targets.keys():
            print(f'{name}: {targets[name]}')
        return 1

    if args.url:
        raw_url = args.url[0]
        url, use_message = parse_url_entry(raw_url)
    else:
        if name in targets.keys():
            value = targets[name]
            while value.startswith(alias_protocol):
                alias_target = value[len(alias_protocol):]
                if alias_target not in targets:
                    print(f'No such a webhook target name: {alias_target}', file=sys.stderr)
                    return 1
                value = targets[alias_target]
            url, use_message = parse_url_entry(value)
        else:
            if name == default_target_name:
                print('Default webhook target name is not defined', file=sys.stderr)
            else:
                print(f'No such a webhook target name: {name}', file=sys.stderr)
            return 1

    text = sys.stdin.read()
    message = build_message_message(text) if use_message else build_card_message(text)

    if args.dry:
        import json
        print(f'url={url}')
        print(json.dumps(message, indent=2, ensure_ascii=False))
        return 0

    try:
        headers = { 'Content-Type': 'application/json' }
        res = requests.post(url, json=message, headers=headers)
        print(f'{res.status_code} {res.reason}')
        return 0 if res.ok else 1
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

if __name__ == '__main__':
    exit(send())
