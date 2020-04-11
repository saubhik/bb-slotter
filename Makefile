build:
	docker build -t slotter . \
	--build-arg FROM_ADDR="${FROM_ADDR}" \
	--build-arg TO_ADDR="${TO_ADDR}" \
	--build-arg EMAIL_PASSWORD="${EMAIL_PASSWORD}" \
	--build-arg CITY1="${CITY1}" \
	--build-arg CITY2="${CITY2}" \
	--build-arg AREA1="${AREA1}" \
	--build-arg AREA2="${AREA2}" \
	--build-arg URL="${URL}" \
	--no-cache
