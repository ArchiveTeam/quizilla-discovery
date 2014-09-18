'''Find valid tags and usernames.


The file will contain things like:

short:12345
user:bookloving101
tag:romance
'''
import gzip
import re
import requests
import string
import sys
import time
import random

DEFAULT_HEADERS = {'User-Agent': 'ArchiveTeam'}


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    output_filename = sys.argv[3]  # this should be something like myfile.txt.gz

    assert start_num <= end_num

    print('Starting', start_num, end_num)

    gzip_file = gzip.GzipFile(output_filename, 'wb')

    for shortcode in check_range(start_num, end_num):
        # Write the valid result one per line to the file
        line = '{0}\n'.format(shortcode)
        gzip_file.write(line.encode('ascii'))

    gzip_file.close()

    print('Done')


def check_range(start_num, end_num):
    '''Check if page exists.

    Each line is like short:12345 or user:bookloving101
    '''

    for num in range(start_num, end_num + 1):
        shortcode = num
        url = 'http://quizilla.teennick.com/quizzes/{0}'.format(shortcode)
        url1 = 'http://quizilla.teennick.com/stories/{0}'.format(shortcode)
        url2 = 'http://quizilla.teennick.com/polls/{0}'.format(shortcode)
        url3 = 'http://quizilla.teennick.com/poems/{0}'.format(shortcode)
        url4 = 'http://quizilla.teennick.com/lyrics/{0}'.format(shortcode)
        counter = 0

        while True:
            # Try 20 times before giving up
            if counter > 20:
                # This will stop the script with an error
                raise Exception('Giving up!')

            try:
                text = fetch(url)
                text1 = fetch1(url1)
                text2 = fetch2(url2)
                text3 = fetch3(url3)
                text4 = fetch4(url4)
            except FetchError:
                # The server may be overloaded so wait a bit
                print('Sleeping... If you see this')
                time.sleep(10)
            else:
                if text:
                    yield 'id:{0}'.format(shortcode)

                    username = extract_handle(text)

                    if username:
                        yield 'user:{0}'.format(username)

                    for tag in extract_tags(text):
                        yield 'tag:{0}'.format(tag)
                elif text1:
                    yield 'id:{0}'.format(shortcode)

                    username = extract_handle(text1)

                    if username:
                        yield 'user:{0}'.format(username)

                    for tag in extract_tags(text1):
                        yield 'tag:{0}'.format(tag)
                elif text2:
                    yield 'id:{0}'.format(shortcode)

                    username = extract_handle(text2)

                    if username:
                        yield 'user:{0}'.format(username)

                    for tag in extract_tags(text2):
                        yield 'tag:{0}'.format(tag)
                elif text3:
                    yield 'id:{0}'.format(shortcode)

                    username = extract_handle(text3)

                    if username:
                        yield 'user:{0}'.format(username)

                    for tag in extract_tags(text3):
                        yield 'tag:{0}'.format(tag)
                elif text4:
                    yield 'id:{0}'.format(shortcode)

                    username = extract_handle(text4)

                    if username:
                        yield 'user:{0}'.format(username)

                    for tag in extract_tags(text4):
                        yield 'tag:{0}'.format(tag)
                break  # stop the while loop

            counter += 1


def fetch(url):
    '''Fetch the URL and check if it returns OK.

    Returns True, returns the response text. Otherwise, returns None
    '''
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    # response doesn't have a reason attribute all the time??
    print('Got', response.status_code, getattr(response, 'reason'))

    if response.status_code == 200:
        # The item exists
        if not response.text:
            # If HTML is empty maybe server broke
            raise FetchError()

        return response.text
    elif response.status_code == 301:
        # Is a non-existing poll
        return
    elif response.status_code == 404:
        # Does not exist
        return
    else:
        # Problem
        raise FetchError()


def extract_handle(text):
    '''Return the page creator from the text.'''
    # Search for something like
    # <dd><a href="/user/bookloving101/profile">BookLoving101</a>
    match = re.search(r'<dd><a\s+href="/user/([^/]+)/profile"', text)

    if match:
        return match.group(1)


def extract_tags(text):
    '''Return a list of tags from the text.'''
    # Search for href="/tags/romance"
    return re.findall(r'"/tags/([^"]+)"', text)

if __name__ == '__main__':
    main()
