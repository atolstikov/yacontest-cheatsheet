import requests


def main():
    server = input()
    port = int(input())
    a = int(input())
    b = int(input())
    response = requests.get(f'{server}:{port}', params={'a': a, 'b': b})
    response.raise_for_status()
    payload = response.json()
    print(*sorted(payload['result']))
    print(payload['check'])


if __name__ == '__main__':
    main()
