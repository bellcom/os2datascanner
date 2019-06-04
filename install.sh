#!/usr/bin/env bash

DIR=$(dirname ${BASH_SOURCE[0]})
VIRTUALENV=./python-env

# Update package registry before installing system dependencies
sudo apt-get update

# System dependencies. These are the packages we need that are not present on a
# fresh Ubuntu install.

SYSTEM_PACKAGES=$(cat "$DIR/doc/SYSTEM_DEPENDENCIES")

for package in "${SYSTEM_PACKAGES[@]}"
do
    sudo apt-get -y install $package
done


# Setup virtualenv, install Python packages necessary to run BibOS Admin.

if [ -e $VIRTUALENV/bin/activate ]
then
    echo "virtual environment already installed" 1>&2
else
    virtualenv -p python3 $VIRTUALENV
fi

source $VIRTUALENV/bin/activate

PYTHON_PACKAGES=$(cat "$DIR/doc/PYTHON_DEPENDENCIES")

for  package in "${PYTHON_PACKAGES[@]}"
do
    pip install $package

    RETVAL=$?
    if [ $RETVAL -ne 0 ]; then
        echo "" 1>&2
        echo "ERROR: Unable to install Python package <$package>." 1>&2
        echo -n "Please check your network connection. " 1>&2
        echo "A remote server may be down - please retry later. " 1>&2
        echo "" 1>&2
        exit -1
    fi
done

pushd django-os2webscanner
python setup.py develop
popd

pushd webscanner_client
python setup.py develop
popd
