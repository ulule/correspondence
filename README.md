# correspondence

A dead simple interface to send SMS messages built with [FastAPI](https://fastapi.tiangolo.com/)
and [SQLAlchemy](https://www.sqlalchemy.org/).

## Requirements

You must install:

* Python 3
* Postgresql
* Redis

On macOS, install [homebrew](https://brew.sh/)

```console
brew install python3 postgresql redis
```

## Installation

Install [uv](https://github.com/astral-sh/uv) first, then run:

```bash
uv sync
```

to install dependencies.

## Install database

To install the database, run:

```bash
make flush
```

it will install the database and its schema.


## Install frontend dependencies

```bash
npm install
```

## Basic commands

### API server

```bash
make run-api
```

### Worker

```bash
make run-worker
```

### Frontend

```bash
npm run watch
```
