#!/bin/bash

#进入monitor mode
set -m

current_path=$(
    cd "$(dirname $0)" || exit
    pwd
)

cd "$current_path" || exit

if [ ! -f "./genzero.yaml" ]; then
    if ! genzero init config; then
        exit 1
    fi
fi

# 会根据yaml配置文件来生成服务的配置文件
if ! genzero start --dev; then
    exit 1
fi
