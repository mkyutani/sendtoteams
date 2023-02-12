# teams-webhook: Microsoft Teams's incoming webhook interface

## Usage

`sendtoteams` sends some text to Microsoft Teams's Incoming Webhook.

Text is given by command line option -t or standard input.

Teams's webhook url must be given by command line option -u or environment variable `TEAMS_WEBHOOK`.
(Webhook url is published in teams client. cf. [Create Incoming Webhooks](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=dotnet))

`sendtoteams` prints http status code.  If the code is `200`, the request is processed successfully.

Some samples as below.

```
$ sendtoteams -t 'hello, world' -u teams-webhook-url
200
$ echo hello, world | sendtoteams -u teams-webhook-url
200
```

Samples using environment variable `TEAMS_WEBHOOK`.

```
$ export TEAMS_WEBHOOK=teams-webhook-url
$ sendtoteams -t 'hello, world'
200
$ echo hello, world | sendtoteams
200
```

`sendtoteams` recognize the first line as a title when the first character is '#'. (tag in twitter)
For example:

* Source text
```
#sendtoteams Send text to Microsoft Teams' Incoming Webhook
✅ Hello, world
🔸 foo
🔸 bar
🔸 baz
```
* Teams' text
![Text in Teams](img/webhook-title-sample.png)


## Install

```
pip3 install git+https://github.com/mkyutani/teams-webhook.git
```

## License

MIT License.
