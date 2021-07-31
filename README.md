# dvsa-practicals

Watch the DVSA site for cancellations of practical driving tests, using Python and Selenium.

The Coronavirus pandemic has hit the driving instruction industry here in the UK particularly hard. As a result of
the various lockdowns and restrictions, there is a backlog of several months for appointments to sit the practical test
(as I write this, there are no available appointments _anywhere for ~4 months_).

To compound the problem, the DVSA (the Government body responsible) appears to have abdicated any sense of
responsibility for appropriately dealing with this problematic situation; meaning there is essentially a complete
free-for-all. If you just happen to be on the website for the right 5 minutes, you _might_ be able to snatch up a
cancellation a few weeks away - rather than months.

Predictably, there are now a variety of services making a quick buck offering notifications when a sooner appointment
becomes available, which irked me a bit, considering it took me a few hours to write this script, which does exactly
the same, and is free for anyone to use.

## Installation

### Pre-requisites

You'll need:

- Python 3.9 or greater
- [Poetry](https://python-poetry.org)

### Setup

- Download and unzip or clone this repo
- `cd` into it and run `poetry install`
  
## Usage

For example, the following will invoke the search:
- using the licence number `SMITH901019JD1AB`
- for test centres near postcode `WC1A`
- using a search date of `2021-10-01`

```shell
dvsa-practicals SMITH901019JD1AB WC1A 2021-10-01
```

At some point in the setup process, you are basically guaranteed to hit a captcha prompt. The program will wait while
you solve the captcha and resume on success. Fortunately, the actual watching bit doesn't appear to be captcha-proofed,
so you should only need to solve one captcha. 

Notifications are implemented very simply, using the [bell character](https://en.wikipedia.org/wiki/Bell_character).
Consult your terminal's instructions on how to make this alert loud and obvious.

Run `dvsa-practicals --help` for more info on other parameters.

## Notifications

This bot allows you to get notifications via email or telegram.
To make use of this feature kindly update all the fields with the relavant data in ```config.py```

```
ENABLE_TELEGRAM=True #For telegram notifications
ENABLE_EMAIL=True #For emails notificaitons
```
Please ensure to configure the ```SMTP``` details for email notifications and ```TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID``` for telegram notifications



## Support

Currently the bot supports new Driving Practical Test checks only. Feel free to contribute.
Looking for new methods to allow checks/cancellations for existing bookings and the ability to auto rebook if available.