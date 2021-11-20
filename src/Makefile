SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

PYTHON = ../env/Scripts/python.exe

.PHONY: all

all: proxy publisher subscriber

# Run Proxy
proxy:
	$(PYTHON) proxy_run.py

# Run a publisher
publisher:
	$(PYTHON) pub_run.py

# Run a subscriber
subscriber:
	$(PYTHON) subscriber.py

# Publish a new message to a given topic
put:
	$(PYTHON) do_put.py

# Get a message from a given topic
get:
	$(PYTHON) do_sub.py get

# Subscribe a new topic
sub:
	$(PYTHON) do_sub.py subscribe

# Unsubscribe a given topic
unsub:
	$(PYTHON) do_sub.py unsubscribe

# Remove generated folders and files
clean:
	rm -rf __pycache__
	rm storage.ser