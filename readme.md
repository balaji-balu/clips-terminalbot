docker run -d --name refund-postgres -e POSTGRES_USER=your_user -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=ecommerce -p 5432:5432 postgres:15

docker exec -it refund-postgres psql -U your_user -d ecommerce
docker cp script.sql refund-postgres:/tmp/script.sql 
docker exec -it refund-postgres psql -U your_user -d ecommerce -f /tmp/script.sql