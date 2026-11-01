#!/usr/bin/env python3
import subprocess
import sys
import time
import urllib.request

URL = 'http://127.0.0.1:7777/?a=1&b=1'


def wait_until_up(timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=1)
            return
        except Exception:
            time.sleep(0.2)
    sys.stderr.write('server did not start\n')
    sys.exit(1)


def main():
    server = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_until_up()
        completed = subprocess.run([sys.executable, 'solution.py'])
        return completed.returncode
    finally:
        server.kill()
        server.wait()


if __name__ == '__main__':
    sys.exit(main())
