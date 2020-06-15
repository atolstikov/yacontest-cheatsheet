import sys
import datetime


if __name__ == '__main__':
    stdout_file = sys.argv[2]

    with open(stdout_file) as f:
        lines = f.readlines()
        last_line = lines[-1].strip().split()
        score = float(last_line[1])
        d = datetime.datetime.now() - datetime.datetime(2020, 2, 29, 3, 0)
        n_days = 0 if d.total_seconds() <= 0 else d.days + 1
        penalty = 1.0 - min(0.5, n_days * 0.1)
        print(score * penalty)
