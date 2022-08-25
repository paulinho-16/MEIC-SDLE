SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

PYTHON = python.exe

.PHONY: proxy publisher subscriber put get sub unsub clean

RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

# Run Proxy
proxy:
	@$(PYTHON) proxy_run.py

# Run a publisher
publisher:
	@$(PYTHON) pub_run.py $(filter-out $@, $(MAKECMDGOALS))

# Run a subscriber
subscriber:
	@$(PYTHON) sub_run.py $(filter-out $@, $(MAKECMDGOALS))

# Publish a new message to a given topic
put:
	@$(PYTHON) exec_command.py $@ $(RUN_ARGS)

# Get a message from a given topic
get:
	@$(PYTHON) exec_command.py $@ $(RUN_ARGS)

# Subscribe a new topic
sub:
	@$(PYTHON) exec_command.py $@ $(RUN_ARGS)

# Unsubscribe a given topic
unsub:
	@$(PYTHON) exec_command.py $@ $(RUN_ARGS)

# Remove generated folders and files
clean:
	find . -name '__pycache__' -exec rm -rf "{}" +;
	rm -f subscriber/storage-*.ser
	rm -rf storage/
	rm -f logger.log