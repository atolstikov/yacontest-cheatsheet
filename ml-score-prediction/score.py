#!/usr/bin/env python3
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

OUT = 'answers.csv'
N_ROWS = 3140


def report(text):
    with open(OUT, 'w', encoding='utf-8') as handle:
        handle.write(text.rstrip() + '\n')


def main():
    try:
        y_pred = pd.read_csv('data.csv', header=None).to_numpy()
    except Exception as exc:
        report('cannot read data.csv: {}'.format(exc))
        return

    if y_pred.shape != (N_ROWS, 1):
        report('incorrect shape: {} instead of {}'.format(tuple(y_pred.shape), (N_ROWS, 1)))
        return

    y_true = pd.read_csv('true_answers.csv', header=0).to_numpy().ravel()
    y_pred = y_pred.ravel()
    value = f1_score(y_true, y_pred)
    points = float(np.clip((value - 0.5) / 0.16, a_min=0.0, a_max=2.0))
    report('{:.10f}'.format(points))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        report('scoring failed: {}'.format(exc))
    sys.exit(0)
