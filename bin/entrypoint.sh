#!/bin/ash
# Make sure we are in build
cd /build/

echo "Wait until database is ready..."
while ! nc -z $DB_HOST 5432
do
	echo "Retrying"
	sleep 5
done

# Prepare the database
invoke db --fixtures --recreate --wait

# Perform test
pytest --cov-report xml:cov.xml --cov-report term --junitxml=xunit.xml --cov=apps --migration
touch /build/up

# Start worker
python3 manage.py runworker -v 2 &

# Start daphne
daphne -b 0.0.0.0 -p 8000 apps.core.asgi:channel_layer -v 2 --proxy-headers
