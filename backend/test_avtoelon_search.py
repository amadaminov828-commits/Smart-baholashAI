import requests
import urllib.parse
from bs4 import BeautifulSoup

query = urllib.parse.quote("Gentra 2017")
url = f"https://avtoelon.uz/avto/?search={query}"
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.text, 'html.parser')
links = [a.get_text(strip=True) for a in soup.find_all('a', href=True) if '/a/show/' in a['href']]

url2 = f"https://avtoelon.uz/avto/?q={query}"
resp2 = requests.get(url2, headers={'User-Agent': 'Mozilla/5.0'})
soup2 = BeautifulSoup(resp2.text, 'html.parser')
links2 = [a.get_text(strip=True) for a in soup2.find_all('a', href=True) if '/a/show/' in a['href']]

with open("C:\\Users\\Asus\\Desktop\\antigravity\\backend\\avtoelon_test.txt", "w", encoding="utf-8") as f:
    f.write("?search=:\n")
    for l in links[:5]: f.write(l + "\n")
    f.write("\n?q=:\n")
    for l in links2[:5]: f.write(l + "\n")
