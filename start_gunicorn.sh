#!/usr/bin/env bash
cd $( dirname $0 )
. ../secrets.sh
[[ ! -d venv ]] && mkdir venv && virtualenv venv
. venv/bin/activate
[[ -f ./requirements.txt ]] && pip install -r ./requirements.txt
[[ -f ./requirements_gunicorn.txt ]] && pip install -r ./requirements_gunicorn.txt
cd ..
gunicorn --timeout 120 --workers 4 --pid ./adminservice.pid --log-level=DEBUG -b 0.0.0.0:5481 adminservice:app
