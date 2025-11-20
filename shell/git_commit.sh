#!/bin/bash
cd /code/CUTeMoL/exercise/
git add -A
git diff --name-only HEAD | tr '\n' ',' | xargs -I {} git commit -a -m "lxw updated {} on `date  "+%Y-%m-%d %H:%M:%S%z"`"
git push origin