SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

PYTHON = python.exe

.PHONY: proxy publisher subscriber put get sub unsub clean

# Run Proxy
proxy:
	@$(PYTHON) proxy_run.py

# Run a publisher
publisher:
	@$(PYTHON) pub_run.py

# Run a subscriber
subscriber:
	@$(PYTHON) sub_run.py

# Publish a new message to a given topic
put: 
	@$(PYTHON) do_put.py $(filter-out $@, $(MAKECMDGOALS))

# Get a message from a given topic
get:
	@$(PYTHON) do_sub.py $(MAKECMDGOALS)

# Subscribe a new topic
sub:
	@$(PYTHON) do_sub.py $(MAKECMDGOALS)

# Unsubscribe a given topic
unsub:
	@$(PYTHON) do_sub.py $(MAKECMDGOALS)

# Remove generated folders and files
clean:
	find . -name '__pycache__' -exec rm -rf "{}" +;
	rm -f subscriber/storage-*.ser
	rm -f storage.pickle