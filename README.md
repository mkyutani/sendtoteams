# teams-webhook: Microsoft Teams's incoming webhook interface

## Usage

`sendtoteams` sends some text to a Microsoft Teams webhook.

The message is read from standard input.

The webhook url must be given by command line option `-u url` or environment variable `TEAMS_WEBHOOK`.
(Webhook url is published in the Teams client. See [Create Incoming Webhooks](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=dotnet))

`sendtoteams` prints the HTTP status code and reason returned by the webhook. The request succeeded when the code is in the `2xx` range.

Some samples as below.

```
$ echo 'hello, world' | sendtoteams -u http://url
200 OK
```

Samples using environment variable `TEAMS_WEBHOOK`.

```
$ export TEAMS_WEBHOOK=http://url
$ echo 'hello, world' | sendtoteams
200 OK
```

### Message format

By default `sendtoteams` sends an Adaptive Card. Prefix the url with `msg:` (also `message:` or `m:`) to send a plain message instead, or `card:` (also `c:`) to make the default explicit. The prefix can be attached to a `-u` value or to any entry in `TEAMS_WEBHOOK`.

* **Card** (default): raw http/https urls in the text become markdown links and newlines are kept as line breaks.
* **Message**: raw http/https urls become `<a href>` anchors and newlines become `<br>`.

```
$ echo 'see http://example.com' | sendtoteams -u msg:http://url
```

### Dry run

`sendtoteams --dry` executes a 'dry run', which prints the resolved url and the JSON payload only instead of sending it to Teams.

Card (default):

```
$ echo 'hello, world' | sendtoteams -u http://url --dry
url=http://url
{
  "text": "hello, world\n",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "padding": "none",
        "body": [
          {
            "type": "TextBlock",
            "text": "hello, world  \n",
            "wrap": true
          }
        ]
      }
    }
  ]
}
```

Message (`msg:` prefix):

```
$ echo 'see http://example.com' | sendtoteams -u msg:http://url --dry
url=http://url
{
  "text": "see <a href=\"http://example.com\">http://example.com</a>"
}
```

### Webhook selection

`sendtoteams` with `-n name` can select one by name in a webhook url list, which is a semicolon separated list of `name=url`, `name=othername` (alias) or a bare `url`. For example, `-u` or `TEAMS_WEBHOOK="foo=http://foo;bar=http://bar;baz=foo;foo"` means (1) `foo` specifies http://foo, (2) `bar` specifies http://bar, (3) `baz` is an alias of foo (so `baz` specifies http://foo), and (4) the bare `foo` becomes the default target. Each url may carry a `msg:`/`card:` format prefix.

`sendtoteams --list` prints the list of the webhook selections (aliases are shown as `alias:name`).

```
$ TEAMS_WEBHOOK='foo=http://foo;bar=msg:http://bar;baz=foo;foo' sendtoteams --list
foo: http://foo
bar: msg:http://bar
baz: alias:foo
default: alias:foo
$ echo 'Hello, world' | TEAMS_WEBHOOK='foo=http://foo;bar=http://bar;baz=foo;foo' sendtoteams -n baz --dry
url=http://foo
{
  "text": "Hello, world\n",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "padding": "none",
        "body": [
          {
            "type": "TextBlock",
            "text": "Hello, world  \n",
            "wrap": true
          }
        ]
      }
    }
  ]
}
```

## Install

```
pip3 install git+https://github.com/mkyutani/teams-webhook.git
```

## License

MIT License.
