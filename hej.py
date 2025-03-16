import requests

PROXY = "http://31.220.15.234:80"
test_url = "http://httpbin.org/ip"

try:
    response = requests.get(
        test_url, proxies={"http": PROXY, "https": PROXY}, timeout=5
    )
    print("Proxy fungerar! Din IP via proxy:", response.json())
except Exception as e:
    print("Proxy fungerar inte:", str(e))
