#!/bin/bash

echo "Please enter the project name in lowercase and with dashes (i.e. django-api): "
read project
find . -type f -print0 | xargs -0 sed -i "s/django\-api/$project/g"

echo "Please enter the project name in title case (i.e. Django API): "
read name
find . -type f -print0 | xargs -0 sed -i "s/Django API/$name/g"