#!/bin/bash

#进入monitor mode
set -m

current_path=$(
    cd "$(dirname $0)" || exit
    pwd
)

cd "$current_path" || exit

name=news

goctl api go --api $name.api --dir ../ --style goZero

sql_file="./news.sql"
goctl model mysql ddl --src "$sql_file" -dir ../model --cache --style goZero