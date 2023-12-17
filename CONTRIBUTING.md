# Contributing

We welcome all types of contributions, such as bug reports, ideas, design, testing, and code.

## Development

To set up a development envoironment, first clone this project to your local development directory and change into the source directory.

### Prerequisites

We recommend using Python 3.11 or later.

We also use the following tools for development.

#### pipx

We recommend using pipx to install the development tools.

- https://pypa.github.io/pipx/installation/

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

### Activate virtual environment

Whenever you develop, make sure you are in the project's virtual environment.

Linux / OSX:

```sh
source .venv/bin/activate
```

Windows:

```sh
.venv\Scripts\activate
```

### Install dependencies

Once you have the above prerequesites installed, install the project development dependencies as follows.

```sh
pip install -r requirements.dev.txt
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

### Create superuser

When starting out with an empty database, after applying migrations, create a superuser as follows.

```sh
python manage.py createsuperuser
```

### Run the server

When all migrations are applied and you have a superuser, run the server as follows.

```sh
python manage.py runserver
```
