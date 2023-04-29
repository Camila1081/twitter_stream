# AWS para Twitter Stream - Kinesis to DynamoDb

## Instalando terraform
Incluir path da pasta do exe na variavel de ambiente

docker run -d -p 80:80 docker/getting-started
aws configure

## enviroment in cmd bat do windows
```bash
setx AWS_ACCESS_KEY_ID <>
setx AWS_SECRET_ACCESS_KEY <>
setx AWS_DEFAULT_REGION us-west-2
````

## Comandos - passo a passo:
```bash
cd terraform
terraform init
#terraform plan -out=plan.out
terraform apply

cd ..
cd docker
docker build -t twitter_produce -f Dockerfile_produce .
docker build -t twitter_consume -f Dockerfile_consume .

docker run -e BEARER_TOKEN="<>" -e AWS_ACCESS_KEY_ID="<>" -e AWS_SECRET_ACCESS_KEY="<>" -t twitter_produce
docker run -e BEARER_TOKEN="<>" -e AWS_ACCESS_KEY_ID="<>" -e AWS_SECRET_ACCESS_KEY="<>" -t twitter_consume

```

## Destruir a infra:

```bash
docker stop twitter_produce
docker stop twitter_consume
docker system prune --force

terraform destroy
```
