TAG:=$(shell date "+%Y%m%d%H%M")

###############################################################################
# HELP / DEFAULT COMMAND
###############################################################################
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## Build the curabase services
	docker build --build-arg IMAGE_VERSION=$(TAG) -t favicon -t favicon:$(TAG) .
	docker tag favicon:$(TAG) curabase/favicon:$(TAG)

.PHONY: push
push: build
	#docker push curabase/favicon:$(TAG)

.PHONY: prod-deploy
prod-deploy: push ## deploy directly to production
	docker save favicon:$(TAG) | bzip2 | pv| ssh prod.m3b 'bunzip2 | docker load'
	ssh deploy@prod.m3b "cd /home/deploy/deployment/containers/favicon && make deploy RELEASE=$(TAG)"

.PHONY: run-prod
run-prod:
	docker run -it \
		--rm \
		-p 8080:8000 \
		--env-file=env \
		favicon:$(TAG)

.PHONY: clean
clean:
	find src/ -type f -name *.pyc -delete
	find src/ -type d -name __pycache__ -exec rm -rf {} \;

.PHONY: mypy
mypy:
	source venv/bin/activate && mypy  --ignore-missing-imports src