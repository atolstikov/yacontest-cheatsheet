#!/usr/bin/python

import simplejson as json
from sys import stdin, stderr, stdout
import traceback
import re
import sys


def getVerdicts(tests, testData):
   verdicts = {}
   for i in tests:
       s = testData[i-1]["verdict"]
       if s not in verdicts:
           verdicts.update({s : 0})
       verdicts.update({s : verdicts[s] + 1})
   return ','.join(['%d %s' % (verdicts[j], j) for j in verdicts])


def getIfHas(d, v):
    if v in d:
       return d[v]
    return None

try:
    testData = json.load(stdin)["tests"]

    important = ["testName", "verdict", "message"]
    tests = [ {j : getIfHas(i,j) for j in important} for i in testData]

    tests.sort(key = lambda x : x ["testName"])
    tests = [ tests[i] for i in range(len(tests)) if i == 0 or tests[i]["testName"] != tests[i-1]["testName"] ]

    answer = re.findall("\$.*\$", tests[0]["message"].replace('\n', ' '))
    if (len(answer) != 0):
        stdout.write(answer[0].replace("$","") + '\n')
        # sys.exit(4)

except Exception as e:
    stdout.write('\n')
    traceback.print_exc(file=stderr)
