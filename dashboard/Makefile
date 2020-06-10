
TARGET=python manage.py
MIGRATIONS_ID=consumption
IMPORTING_CSV=../data/

migrate:
	${TARGET} migrate ${MIGRATIONS_ID}

reset_migrate:
	${TARGET} migrate ${MIGRATIONS_ID} zero

make_migrate:
	${TARGET} makemigrations

show_migrate:
	${TARGET} migrate showmigrations

import:
	${TARGET} import
