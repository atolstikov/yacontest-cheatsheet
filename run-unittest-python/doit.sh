#!/bin/bash
OUT=expression.py

mv $filename $OUT || exit 1

echo $OUT
cat $OUT
