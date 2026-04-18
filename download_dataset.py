import urllib.request
import json
import time

try:
    req = urllib.request.Request('https://api.github.com/search/code?q=filename:spotify-2023.csv', headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    if data['items']:
        item = data['items'][0]
        # Xây dựng url raw
        # Note: github search API không chắt lọc branch, thường là 'main' hoặc 'master'
        # Hoặc dùng url html_url và thay thế
        html_url = item['html_url']
        raw_url = html_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        print(f"Downloading from {raw_url}...")
        urllib.request.urlretrieve(raw_url, 'spotify-2023.csv')
        print("Success!")
    else:
        print("Not found")
except Exception as e:
    print(f"Error: {e}")
