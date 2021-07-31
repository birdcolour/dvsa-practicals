import functools
import os
import subprocess
import time
from datetime import datetime

import click as click
import numpy as numpy
from selenium import webdriver


import requests
import smtplib
from email.mime.text import MIMEText

import config


# Timing
queue_pause = 10
captcha_pause = 10
result_pause = 120
pageload_pause = 5


# I'm too lazy to do user input properly; using keyboard interrupts via this selenium hack:
# https://stackoverflow.com/a/62430234

def new_start(*args, **kwargs):
    def preexec_function():
        os.setpgrp()
    default_Popen = subprocess.Popen
    subprocess.Popen = functools.partial(
        subprocess.Popen, preexec_fn=preexec_function)
    try:
        new_start.default_start(*args, **kwargs)
    finally:
        subprocess.Popen = default_Popen


new_start.default_start = webdriver.common.service.Service.start
webdriver.common.service.Service.start = new_start


def random_sleep(lam, maximum=300):
    """Sleep for a length of time sampled from a poisson distribution, capped at a maximum."""
    time.sleep(min(numpy.random.poisson(lam, None), maximum))


def submit(driver, id_='driving-licence-submit'):
    """Submit form and continue."""
    driver.find_element_by_id(id_).click()
    pause_on_captcha(driver)


def notify(msg):
    msg += '\nHead over to https://driverpracticaltest.dvsa.gov.uk/ to book now'
    if config.ENABLE_TELEGRAM:
        response = requests.post(
            url='https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage'.format(
                config.TELEGRAM_BOT_TOKEN),
            data={'chat_id': config.TELEGRAM_CHAT_ID, 'text': msg}
        ).json()
    if config.ENABLE_EMAIL:
        message = {}
        message = MIMEText(msg, 'plain', 'utf-8')
        message['Subject'] = "Driving Test Availability Notification"
        message['From'] = config.smtp['sender']
        message['To'] = config.smtp['recipient']

        # Port 587 works with most E-mail SMTP connections
        server = smtplib.SMTP(config.smtp['server'], 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(config.smtp['login'], config.smtp['password'])
        server.sendmail(config.smtp['sender'], config.smtp['recipient'], message.as_string())
        server.quit()
    click.echo('\a')
    click.echo(msg)


def captcha_present(driver):
    return bool(driver.find_elements_by_css_selector('iframe#main-iframe'))


def pause_on_captcha(driver):
    """If we got redirected to a Captcha, pause and notify for a human to solve."""
    driver.implicitly_wait(pageload_pause)
    if captcha_present(driver):
        notify('Captcha detected, please solve to continue...')
        while captcha_present(driver):
            random_sleep(captcha_pause)


def setup(driver, licence, postcode, search_date, extended, special):
    """Take a driver and get to the results page."""
    # Load the start page
    driver.get('https://driverpracticaltest.dvsa.gov.uk/application')
    pause_on_captcha(driver)

    # Sleep while in queue
    while str(driver.current_url).startswith('https://queue'):
        random_sleep(queue_pause)

    pause_on_captcha(driver)

    # Select car (manual and automatic)
    driver.find_element_by_id('test-type-car').click()

    # Fill out form 1 with licence, extended and special flags
    # Enter licence no
    driver.find_element_by_id('driving-licence').send_keys(licence)
    driver.find_element_by_id(
        'extended-test-' + ('yes' if extended else 'no')).click()
    driver.find_element_by_id(
        'special-needs-' + ('add' if special else 'none')).click()
    submit(driver)

    # Fill out form 2 with search date (DD/MM/YY), instructor number (not implemented)
    driver.find_element_by_id(
        'test-choice-calendar').send_keys(search_date.strftime('%d/%m/%Y'))
    submit(driver)

    # Fill out form 3 with postcode
    driver.find_element_by_id('test-centres-input').send_keys(postcode)
    submit(driver, id_='test-centres-submit')

    return driver


def check_for_slots(driver, notify_date):
    """
    Once at the results page, check if any results need to be reported.

    The date text (in the h5 tag) will be either of:
    - "&nbsp;–&nbsp;No dates found"
    - "&nbsp;–&nbsp;available tests around DD/MM/YYYY"
    """

    headings = '.test-centre-results > li > a > div > span'
    for centre_heading, date_heading in zip(
        driver.find_elements_by_css_selector(headings + ' > h2'),
        driver.find_elements_by_css_selector(headings + ' > h5'),
    ):
        try:
            earliest = datetime.strptime(
                date_heading.text.split()[-1], '%d/%m/%Y')
        except ValueError:
            pass
        else:
            if earliest < notify_date:
                notify(
                    f'Earliest available test at {centre_heading.text} is on {earliest.isoformat()}.')


@click.command()
@click.argument('licence')
@click.argument('postcode')
@click.argument(
    'search_date',
    type=click.DateTime(),
    required=False,
    default=datetime.today(),
)
@click.option(
    '-n', '--notify-date',
    type=click.DateTime(),
    required=False,
    help='Notify date - only notify of available tests before this date. If not specified, defaults to the search date.'
)
@click.option('-e', '--extended', is_flag=True, help='Search for extended tests, if mandated by the courts')
@click.option('-s', '--special', is_flag=True, help='Search for tests with special requirements')
def main(licence, postcode, search_date, notify_date, extended, special):
    """
    Search for the earliest available DVSA practical driving tests.

    LICENCE is your Driving Licence Number.

    POSTCODE is the area to search for test centres.

    SEARCH_DATE is the date around which to search; defaults to today.
    """
    if not notify_date:
        notify_date = search_date
    driver = webdriver.Firefox()
    click.echo('Setting up...')
    setup(driver, licence, postcode, search_date, extended, special)
    click.echo('Searching...')
    click.echo(
        'The browser page will now refresh every few minutes, and check for new tests.')
    click.echo(
        'If you are notified of a test and you want to book it, press CTRL-C in the console to stop refreshing.')
    click.echo(
        "When you're done booking it, press CTRL-C in the console again to close the browser.")

    while True:
        try:
            check_for_slots(driver, notify_date)
            driver.refresh()
            pause_on_captcha(driver)
            random_sleep(result_pause)
        except KeyboardInterrupt:
            click.echo('Page refreshing is now off.')
            click.echo('Book before your slot disappears!')
            break

    while True:
        try:
            time.sleep(1000)
        except KeyboardInterrupt:
            click.echo('All done.')
            click.echo('Good luck on the test!')
            driver.quit()
            break
