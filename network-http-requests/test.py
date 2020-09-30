import subprocess
import time

if __name__ == '__main__':
    p1 = subprocess.Popen(["python3", "server.py"], stdout=subprocess.PIPE)
    time.sleep(5)

    # run contestant's solution
    import solution

    p1.kill()
