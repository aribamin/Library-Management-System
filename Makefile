# Makefile

# Default target executed when no arguments are given to make.
default: run

# Target for creating and populating the database.
setup_db:
	sqlite3 prj-database.db < prj_create.sql
	sqlite3 prj-database.db < jen_populate.sql

# Target for running the main Python script.
run: setup_db
	python3 jen_main.py prj-database.db

# Phony targets are not files.
.PHONY: default setup_db run

