#!/bin/bash

set -x 

current_path=$(pwd)
src_path=${current_path}/src
dist_path=${current_path}/dist

rm -rf $dist_path
mkdir -p $dist_path

for pkgDir in "" core zos_console zos_files zos_jobs zos_tso zosmf; do
    cd ${src_path}/$pkgDir
    rm -rf build/ dist/
    python setup.py sdist bdist_wheel
    mv dist/* $dist_path
done
