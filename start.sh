#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset




python ./tender_service/manage.py migrate --noinput
python ./tender_service/manage.py runserver