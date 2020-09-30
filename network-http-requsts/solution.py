import requests


server = input()
port = int(input())
a = int(input())
b = int(input())

resp = requests.get(f"{server}:{port}", params={"a": a, "b": b})
print(*sorted(resp.json()["result"]))
print(resp.json()["check"])
