
TARGET=python manage.py
APP_NAME=consumption
IMPORTING_CSV=../data/
HOST=localhost
PORT=10000

import:
	${TARGET} importer

#
# Short cut commands
#
init: make_migrate migrate
zero: reset_migrate

#
# Basic commands
#
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

#
# Ordered test commands by priority
#
test_1:
	${TARGET} test ${APP_NAME}.tests.test_aggregations

test_2:
	${TARGET} test ${APP_NAME}.tests.test_importer

test_3:
	${TARGET} test ${APP_NAME}.tests.test_user

test_4:
	${TARGET} test ${APP_NAME}.tests.test_consumption

test_5:
	${TARGET} test ${APP_NAME}.tests.test_unique
