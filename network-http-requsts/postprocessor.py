#!/usr/bin/python3

import json
import sys
import traceback

try:
    # Стоимость задачи
    max_value = 100
    # Если different=True, то оценка ставится пропорционально пройденным тестам,
    # исключая samples
    different = False
    testData = json.load(sys.stdin)["tests"]
    important = ["testName", "verdict", "testsetName"]
    tests = [{j: i.get(j, None) for j in important} for i in testData]
    tests.sort(key=lambda x: x["testName"])
    if different:
        tests = [tests[i] for i in range(len(tests)) if
                 (i == 0 or tests[i]["testName"] != tests[i - 1]["testName"]) and tests[i]["testsetName"] != 'samples']
    else:
        tests = [tests[i] for i in range(len(tests)) if (i == 0 or tests[i]["testName"] != tests[i - 1]["testName"])]
    all_tests = len(tests)
    ok = len(list(filter(lambda x: x["verdict"] == "ok", tests)))
    if all_tests == 0:
        mark = 0
    elif different:
        mark = round(max_value * ok / all_tests)
    else:
        mark = 0 if ok < all_tests else max_value

    sys.stdout.write("{}\n".format(mark))
except Exception as e:
    sys.stdout.write('0\n')
    traceback.print_exc(file=sys.stderr)
    sys.exit(5)
