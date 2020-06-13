
TARGET=python manage.py
MIGRATIONS_ID=consumption
IMPORTING_CSV=../data/
HOST=localhost
PORT=10000

import:
	${TARGET} import

#Short commands
init: make_migrate migrate
zero: reset_migrate

migrate:
	${TARGET} migrate ${MIGRATIONS_ID}

make_migrate:
	${TARGET} makemigrations

reset_migrate:
	${TARGET} migrate ${MIGRATIONS_ID} zero

show_migrate:
	${TARGET} showmigrations

server:
	${TARGET} runserver ${HOST}:${PORT}
