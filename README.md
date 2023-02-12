# teams-webhook: Microsoft Teams's incoming webhook interface

## Usage

`sendtoteams` sends some text to Microsoft Teams's Incoming Webhook.

Text is given by command line option -t or standard input.
Teams's webhook url must be given by command line option -u or environment variable TEAMS_WEBHOOK.
(ref. [Create Incoming Webhooks](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=dotnet))

`sendtoteams` prints http status code.  If the code is `200`, the request is processed successfully.

Some samples as below.

```
$ sendtoteams -t 'hello, world' -u teams-webhook-url
200
$ echo hello, world | sendtoteams -u teams-webhook-url
200
```

Samples using environment variable.

```
$ export TEAMS_WEBHOOK=teams-webhook-url
$ sendtoteams -t 'hello, world'
200
$ echo hello, world | sendtoteams
200
```

## Install

```
pip install git+git@github.com:mkyutani/teams-webhook.git
```

## License

MIT License.
