build:
	docker build -t slotter .

bash:
	docker run --env-file '.env' -d --name test-slotter slotter tail -f /dev/null
	docker exec -it test-slotter bash