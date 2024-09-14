ifeq (revision,$(firstword $(MAKECMDGOALS)))
	# use the rest as arguments for run
	RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
	# ... and turn them into do-nothing targets
	$(eval $(RUN_ARGS):;@:)
endif


start:
	python -m src.main

st:
	ruff . --fix
