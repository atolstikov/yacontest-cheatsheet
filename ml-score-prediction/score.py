# encoding=utf-8

import sys
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
import pickle


if __name__ == '__main__':
    target_path = 'true_answers.csv'
    submitted_path = 'data.csv'

    try:
        y_pred = pd.read_csv(submitted_path, header=None).values
    except Exception as e:
        print("$Error while reading answer file: " + str(e) + "$", file=open("answers.csv", "w"))
        sys.exit(0)

    try:
        how_many = 3140

        if y_pred.shape != (3140,1):
            raise ValueError('$incorrect shape: {} instead {}$'.format(y_pred.shape, (3140,1)))

        y_true = pd.read_csv(target_path, header=0).values
        f1_score = f1_score(y_true, y_pred)

    except ValueError as e:
        print("$Error while validating .csv file: " + str(e) + "$", file=open("answers.csv", "w"))
        sys.exit(0)

    print(np.clip((f1_score - 0.5)/0.16,a_min=0., a_max=2.), file=open("answers.csv", "w"))
