# README

The project is **async REST API made on FastAPI**, which uses **PostgreSQL** and **SQLAlchemy async** for its management

## Setup

You can build docker-compose (in project's root directory):
```sh
docker compose -f 'docker-compose.yaml' build
```

Then you can run containers:
```sh
docker compose up
```

Also you may create an `.env` file with secret data:
```ini
POSTGRES_USER       = testuser      # login for PostgreSQL
POSTGRES_PASSWORD   = qwertyuiop    # password for PostgreSQL
POSTGRES_DB         = testdb        # name of database
SECRET              = sdfghjkl      # secret for JWT encoding
```

## Fill database with test data

To fill DB with test data, you can run the `db_init.sh` script (in project's root directory):
```sh
./db_init.sh
```

## Endpoints

There are several groups of endpoints available, you can find them once you run the application: [http://localhost:8000/docs](http://localhost:8000/docs)
