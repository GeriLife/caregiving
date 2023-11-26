# Contributing

We welcome all types of contributions, such as bug reports, ideas, design, testing, and code.

## Development

To set up a development envoironment, first clone this project to your local development directory and change into the source directory.

### Prerequisites

#### pipx

We recommend using pipx to install the development tools.

- https://pypa.github.io/pipx/installation/

#### Poetry

We currently use Poetry to manage project dependencies.

```sh
pipx install poetry
```

#### Pre-commit

We use pre-commit to run various code quality commands prior to each commit.

Install:

```sh
pipx install pre-commit
```

Activate (in the project directory):

```sh
pre-commit install
```

### Install dependencies

Once you have the above prerequesites installed, install the project dependencies as follows.

```sh
poetry install
```

### Activate virtual environment

Whenever you develop, make sure you are in the project virtual environment.

```sh
poetry shell
```

### Migrations

When starting with an empty database or making changes to database models, be sure to make the migrations.

```sh
python manage.py makemigrations
```

When starting out the project or when there are unapplied migrations, apply the database migrations as follows.

```sh
python manage.py migrate
```

### Create superuse

When starting out with an empty database, after applying migrations, create a superuser as follows.

```sh
python manage.py createsuperuser
```

### Run the server

When all migrations are applied and you have a superuser, run the server as follows.

```sh
python manage.py runserver
```
