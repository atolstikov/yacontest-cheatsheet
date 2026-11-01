#!/bin/bash
OUT=expression.py
TMP=$(mktemp ./upload.XXXXXX) || exit 1

cat "${filename}" > "$TMP" || exit 1
rm -f "${filename}"
cat "$TMP" > "$OUT" || exit 1
rm -f "$TMP"
