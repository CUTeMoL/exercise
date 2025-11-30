#!/bin/bash
cd /code/CUTeMoL/exercise/
git add -A
git diff --name-only HEAD |  paste -sd ',' | xargs -I {} git commit -a -m "`git config --get user.name` updated {} on `date  "+%Y-%m-%d %H:%M:%S%z"`"
git push origin