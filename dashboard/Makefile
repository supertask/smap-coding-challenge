
TARGET=python manage.py
MIGRATIONS_ID=consumption
IMPORTING_CSV=../data/

import:
	${TARGET} import

init: make_migrate migrate

migrate:
	${TARGET} migrate ${MIGRATIONS_ID}

make_migrate:
	${TARGET} makemigrations

reset_migrate:
	${TARGET} migrate ${MIGRATIONS_ID} zero

show_migrate:
	${TARGET} showmigrations

