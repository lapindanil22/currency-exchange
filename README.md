# Currency Exchange

## Run app

### With Uvicorn
```
cd src
uvicorn main:app
```

### With Docker

#### Create Docker image
```
docker build -t currency-exchange .
```

#### Run Docker container
```
docker run -p 8000:8000 currency-exchange
```
