build:
	docker build -t bb-slotter . \
	--build-arg FROM_ADDR="${FROM_ADDR}" \
	--build-arg EMAIL_PASSWORD="${EMAIL_PASSWORD}" \
	--no-cache

run:
	docker run --name=bb-slotter-service -v /dev/shm:/dev/shm bb-slotter:latest
