Start postgres docker container 
```sh
docker run -d --name refund-postgres -e POSTGRES_USER=your_user -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=ecommerce -p 5432:5432 postgres:15
```
Run psql on postgres container
```
docker exec -it refund-postgres psql -U your_user -d ecommerce
```

Copy sql script to docker and execute the sql script
```
docker cp script.sql refund-postgres:/tmp/script.sql 
docker exec -it refund-postgres psql -U your_user -d ecommerce -f /tmp/script.sql
```
Run the Terminal Bot
```
python pot.py
```
Open terninal, search the bot (ex. Bb). select .

Enter `/start` 

This message will come as response

**Welcome to the Refund Bot!**
**Send an order ID to check refund eligibility**.

Enter order no( ex: 1)