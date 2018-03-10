# Py-DS - Python Dynatrace Synthetic
[![Build Status](https://travis-ci.org/micha-k/py-dynasynthetic.svg?branch=master)](https://travis-ci.org/micha-k/py-dynasynthetic)
[![Coverage Status](https://coveralls.io/repos/github/micha-k/py-dynasynthetic/badge.svg?branch=master)](https://coveralls.io/github/micha-k/py-dynasynthetic?branch=master)

## Structure

This repository contains 
* dynasynthetic/DynatraceDatafeedAPI - a low level abstraction of the dynatrace datafeed api
* dynasynthetic(DynatraceSyntheticAPI - a high level abstraction representing various use cases, including the threshhold evaluation
* dynasynthetic/CommandlineClient - a commandline application, acting as a consumer of the DynatraceSyntheticAPI
* dynasynthetic_cli.py - executable for the commandline client
* check_dynasynthetic.py - executable to run the commandline client in a nagios check style


## Setup development environment

Create virtual environment for development

        virtualenv -p python2.7 venv
        
Use virtuel environment 
        
        source venv/bin/activate

Run tests using tox

        tox

## Use application

Set your credentials as env variables

        export DS_USER='your username'; DS_PASS=$(echo -n 'your password' | md5)
        
Use cli application (example: list all metrics)

        ./dynasynthetic_cli.py list -l metrics -u $DS_USER -p $DS_PASS

Perform nagios check in a metric

        ./check_dynasynthetic.py monitor -m uxtme -s 12345 -c 3000 -w 2000  -u $DS_USER -p $DS_PASS