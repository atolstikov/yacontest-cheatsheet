#!/bin/bash
OUT=data.csv

cat "${filename}" > $OUT || exit 1

echo $OUT
head $OUT
