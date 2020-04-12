build:
	docker build -t bb-slotter . \
	--build-arg FROM_ADDR="${FROM_ADDR}" \
	--build-arg EMAIL_PASSWORD="${EMAIL_PASSWORD}" \
	--build-arg URL="${URL}" \
	--no-cache
