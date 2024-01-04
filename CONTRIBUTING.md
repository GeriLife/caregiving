# Contributing

We welcome all types of contributions,
such as bug reports, ideas, design, testing, and code.

- [Contributing](#contributing)
  - [Community Discussions](#community-discussions)
  - [Feature Requests](#feature-requests)
  - [Reporting Bugs](#reporting-bugs)
  - [Development](#development)
    - [Prerequisites](#prerequisites)
      - [pipx](#pipx)
      - [Pre-commit](#pre-commit)
    - [Activate virtual environment](#activate-virtual-environment)
    - [Install dependencies](#install-dependencies)
    - [Migrations](#migrations)
    - [Create superuser](#create-superuser)
    - [Run the server](#run-the-server)

## Community Discussions

Join our community discussions to share ideas, ask questions, or provide feedback:

Navigate to the Discussions tab in the GitHub repository.
Choose a relevant category for your discussion.
Start a new discussion or contribute to an existing one.
We value your input and look forward to engaging with you in our community.

## Feature Requests

We're always open to new ideas and improvements to our project. To request a feature:

Go to the Issues tab in the GitHub repository.
Click New Issue.
Select the Feature Request template.
Provide a detailed description of the feature and its benefits.
Submit your request.
We appreciate your suggestions and will consider each one carefully.

## Reporting Bugs

If you encounter a bug in the project, please help us by reporting it. To report a bug:

Go to the Issues tab in the GitHub repository.
Click New Issue.
Choose the Bug Report template.
Fill in the template with as much detail as possible to help us understand and reproduce the bug.
Submit the issue.
Your detailed reports are invaluable in helping us fix issues and improve the project.

## Development

To set up a development environment, first, clone this project to your local development
directory and `cd` into the source directory.

### Prerequisites

We recommend using Python 3.11 or later.

We also use the following tools for development.

#### pipx

We recommend using [pipx](https://pypa.github.io/pipx/installation/) to
install the development tools.

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

Once you have the above prerequisites installed, install the project development
dependencies as follows.

```sh
pip install -r requirements.dev.txt
```

### Migrations

When starting with an empty database or making changes to database models,
be sure to make the migrations.

```sh
python manage.py makemigrations
```

When starting the project or when there are unapplied migrations, apply the
database migrations as follows.

```sh
python manage.py migrate
```

### Create superuser

When starting with an empty database, after applying migrations,
create a superuser as follows.

```sh
python manage.py createsuperuser
```

### Run the server

When all migrations are applied and you have a superuser, run the server as follows.

```sh
python manage.py runserver
```
