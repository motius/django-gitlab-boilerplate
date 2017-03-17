Django Meetup
==========

Install and run locally
-----------------------

In preparation you will need Python >=3.4, virtualenv, and pip installed. You can then launch the build process:

    sudo pip install invoke
    invoke main --env=dev

After the build succeeds, you should be able to activate the virtual environment and launch the development server:

    source ./env/bin/activate
    python manage.py runserver

You can run tests with pytest after activating the virtualenv:

    pytest


Install and run in Docker
-------------------------

Install docker-engine and docker-compose then login with your Gitlab credentials and run compose:

    docker-compose build --no-cache
    docker-compose up -d

To run tests:

    docker-compose run app invoke test

To launch a shell in your app:

    docker-compose run app /bin/ash

Use .gitlab-ci.yml
------------------

**.gitlab-ci.yml**
- Define stages (prepare, install ..)
- Define jobs (clean, dependencies ..)

**docker-compose.yml**
- Using variables defined in .env
- Defining the services need to run the django app

**.dockerignore**
- Dont copy folder like .git to the containers

**.env**
- Define all the need environment variables for local builds

Log in
------

After launching the server go to http://127.0.0.1:8000/admin/ and log in with user `admin`, password `admin`.
