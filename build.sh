#!/bin/bash

set -x 

current_path=$(pwd)
src_path=${current_path}/src

cd ${src_path}
rm -r build/ dist/
rm -r core/build/ core/dist/
rm -r zos_console/build/ zos_console/dist/
rm -r zos_files/build/ zos_files/dist/
rm -r zos_jobs/build/ zos_jobs/dist/
rm -r zos_tso/build/ zos_tso/dist/
rm -r zosmf/build/ zosmf/dist/

python3 setup.py sdist bdist_wheel

cd ${src_path}/core
python3 setup.py sdist bdist_wheel
cd ${src_path}/zos_console
python3 setup.py sdist bdist_wheel
cd ${src_path}/zos_files
python3 setup.py sdist bdist_wheel
cd ${src_path}/zos_jobs
python3 setup.py sdist bdist_wheel
cd ${src_path}/zos_tso
python3 setup.py sdist bdist_wheel
cd ${src_path}/zosmf
python3 setup.py sdist bdist_wheel




