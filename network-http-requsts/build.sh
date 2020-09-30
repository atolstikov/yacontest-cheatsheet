#!/bin/sh
if [ ! -f solution.py ]; then mv $filename solution.py || true; fi
rm -rf __pycache__
/usr/bin/python3 check.py