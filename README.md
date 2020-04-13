# bb-slotter
Get email alerts for delivery slots in BB :email: :dark_sunglasses:

Easily extensible to:

- support multiple email recipients
- support multiple cities and pin codes

## `bb-slotter` in action

Docker container running in AWS EC2 instance:

![image-20200412122911322](./screenshots/image-20200412122911322.png)

## Email alert example

![image-20200412122335908](./screenshots/image-20200412122335908.png)

## Building image

These environment variables must be present while building the (executable) docker image using `make build`.

```bash
FROM_ADDR=...
EMAIL_PASSWORD=...
URL=https://www.bigbasket.com/pd/241600/tata-salt--iodized-1-kg-pouch/
```

Also, before building image, `subscribers.json` file is required.
Example:
```json
[
  {
    "city": "xyz",
    "area": "xyz",
    "email": "xyz@abc.com"
  },
  ...
]
```

## Running the image

```bash
docker run -v /dev/shm:/dev/shm bb-slotter:latest --name bb-slotter-service
```

We need to mount the host's shared memory, otherwise we might encounter crashes.

## Disclaimer

For educational purposes. BigBasket T&C [here](https://www.bigbasket.com/terms-and-conditions/).