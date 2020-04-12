# bb-slotter
Get email alerts for delivery slots in BB :email: :dark_sunglasses:

Easily extensible to:

- support multiple email recipients
- support multiple cities and pin codes

---

#### `bb-slotter` in action

Docker container running in AWS EC2 instance:

![image-20200412122911322](./screenshots/image-20200412122911322.png)

---

#### Email alert example

![image-20200412122335908](./screenshots/image-20200412122335908.png)

---

#### Example of env vars

These variables must be present while building the (executable) docker image.

```bash
FROM_ADDR=...
TO_ADDR=...
EMAIL_PASSWORD=...
CITY1=...
AREA1=...
CITY2=...
AREA2=...
URL=https://www.bigbasket.com/pd/241600/tata-salt--iodized-1-kg-pouch/
```

---

#### Disclaimer

For educational purposes. BigBasket T&C [here](https://www.bigbasket.com/terms-and-conditions/).