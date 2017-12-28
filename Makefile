# this should be defined from environment vars, but if not, then we punt
ifndef IMAGE_NAME
	IMAGE_NAME := curabase/favicon-getter
endif

# This is problematic because it only works if you have semver installed
IMAGE_VERSION := $(shell semver.sh bump patch)
DOCKER_RUN := docker run --rm -v $$PWD/src:/usr/src/app $(IMAGE_NAME)
DOCKER_TAG := $(IMAGE_NAME):$(IMAGE_VERSION)

DOCKER_DEV := $(IMAGE_NAME):latest
DOCKER_RUN_DEV := docker run --rm -v $$PWD/src:/usr/src/app $(DOCKER_DEV)

.PHONY: build
build:
	docker build --build-arg IMAGE_VERSION=$(IMAGE_VERSION) -t $(DOCKER_TAG) .

.PHONY: build-dev
build-dev:
	docker build --build-arg IMAGE_VERSION=$(shell git describe --tags) -t $(DOCKER_DEV) .

.PHONY: run
run:
	docker run -it --rm \
		-p 5000:5000 \
		-e SENTRY_DSN=$(shell cat .sentry_dsn) \
		$(DOCKER_TAG) $(CMD)

.PHONY: run-debug
run-debug:
	mkdir -p icons
	docker run -it --rm \
		-v $$PWD/icons:/icons \
		-v $$PWD/src:/usr/src/app \
		-w /usr/src/app \
		-p 5000:5000 \
		-e DEBUG=True \
		-e SENTRY_DSN=$(shell cat .sentry_dsn) \
		$(DOCKER_DEV) python app.py

.PHONY: shell
shell:
	mkdir -p icons
	docker run -it --rm \
		-v $$PWD/icons:/icons \
		-v $$PWD/src:/usr/src/app \
		-w /usr/src/app \
		-e DEBUG=True \
		-e SENTRY_DSN=$(shell cat .sentry_dsn) \
		$(DOCKER_DEV) /bin/bash


.PHONY: test
test:
	$(DOCKER_RUN) pytest

.PHONY: test
test-dev:
	$(DOCKER_RUN_DEV) pytest


.PHONY: clean
clean:
	find src/ -type f -name *.pyc -delete
	find src/ -type d -name __pycache__ -exec rm -rf {} \;

# this make target is run on the ci-server. it may not run successfully on
# your local machine
.PHONY: ci-deploy
ci-deploy: build
	@echo "****************"
	@echo "Running tests..."
	@echo "****************"
	docker run --rm $(IMAGE_NAME) pytest

	@echo "***************************"
	@echo "Tagging and pushing repo..."
	@echo "***************************"
	git tag $(IMAGE_VERSION)
	git push origin $(IMAGE_VERSION)

	@echo "***********************"
	@echo "Pushing docker image..."
	@echo "***********************"
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS)
	docker push $(DOCKER_TAG)

	@echo "************"
	@echo "Deploying..."
	@echo "************"
	ssh-keyscan $(DOKKU_HOST) >> /$(HOME)/.ssh/known_hosts
	ssh $(DOKKU_DEPLOY_USER)@$(DOKKU_HOST) pull $(IMAGE_NAME):$(IMAGE_VERSION)
	ssh $(DOKKU_DEPLOY_USER)@$(DOKKU_HOST) tag $(IMAGE_NAME):$(IMAGE_VERSION) dokku/$(DOKKU_APP_NAME):$(IMAGE_VERSION)
	ssh dokku@$(DOKKU_HOST) tags:deploy $(DOKKU_APP_NAME) $(IMAGE_VERSION)

