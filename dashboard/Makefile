
TARGET=python manage.py
APP_NAME=consumption
IMPORTING_CSV=../data/
HOST=localhost
PORT=10000

import:
	${TARGET} import

#Short commands
init: make_migrate migrate
zero: reset_migrate

migrate:
	${TARGET} migrate ${APP_NAME}

make_migrate:
	${TARGET} makemigrations

reset_migrate:
	${TARGET} migrate ${APP_NAME} zero

show_migrate:
	${TARGET} showmigrations

server:
	${TARGET} runserver ${HOST}:${PORT}

test:
	${TARGET} test ${APP_NAME}
