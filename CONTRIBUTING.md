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
      - [UV Package Manager](#uv-package-manager)
      - [Pre-commit](#pre-commit)
    - [Activate virtual environment](#activate-virtual-environment)
    - [Install dependencies](#install-dependencies)
    - [Migrations](#migrations)
    - [Create superuser](#create-superuser)
    - [Run the server](#run-the-server)
  - [Package Management with UV](#package-management-with-uv)
    - [Adding New Dependencies](#adding-new-dependencies)
    - [Benefits of UV](#benefits-of-uv)
    - [Updating Dependencies](#updating-dependencies)
    - [Other Useful UV Commands](#other-useful-uv-commands)
  - [Privacy and Data Protection Guidelines](#privacy-and-data-protection-guidelines)

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

#### UV Package Manager

We use [uv](https://github.com/astral-sh/uv), a modern Python package manager built for speed and reliability. Install it using pipx:

```sh
pipx install uv
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

### Activate virtual environment

Whenever you develop, make sure you are in the project's virtual environment.

Create a virtual environment using UV:

```sh
uv venv .venv
```

Linux / OSX:

```sh
source .venv/bin/activate
```

Windows:

```sh
.venv\Scripts\activate
```

### Install dependencies

Once you have the above prerequisites installed, install the project dependencies using UV.

For production dependencies:

```sh
uv sync
```

For development dependencies (includes testing tools):

```sh
uv sync --dev
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

## Package Management with UV

### Adding New Dependencies

To add a new dependency to the project:

```sh
# Add a regular dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Add a dependency with a specific version
uv add "package-name>=1.0,<2.0"
```

These commands will automatically update your pyproject.toml file and create/update the lock file.

### Benefits of UV

UV provides several advantages over traditional package management tools:

- **Speed**: UV is dramatically faster at resolving and installing dependencies
- **Reliability**: Consistent installations across environments with lock file support
- **Dependency Groups**: Cleaner separation between production and development dependencies
- **Modern Features**: Native support for PEP 517/518 standards with pyproject.toml
- **Unified Interface**: Single tool for Python version management and package management

### Updating Dependencies

To update dependencies to their latest compatible versions:

```sh
# Update all dependencies
uv sync --upgrade

# Update specific dependency
uv add --upgrade package-name
```

### Other Useful UV Commands

```sh
# View dependency tree
uv tree

# Lock dependencies without installing
uv lock

# Run a script within the project environment
uv run python manage.py runserver

# Check for outdated packages
uv list --outdated

# Remove a dependency
uv remove package-name
```

## Privacy and Data Protection Guidelines

As an open-source community committed to upholding the highest standards of privacy and data security, we align our practices with principles derived from the General Data Protection Regulation (GDPR) and other similar privacy frameworks. While some GDPR principles are more relevant at an organizational level, many can be directly applied to software development, especially in features involving user data. Below are key guidelines that contributors should follow:

1. **Data Minimization:** Only collect data that is essential for the intended functionality. Avoid unnecessary collection of personal information. When in doubt, less is more.

2. **Consent and Transparency:** Ensure that the software provides clear mechanisms for obtaining user consent where applicable. Users should be informed about what data is collected, why it is collected, and how it will be used.

3. **Anonymization and Pseudonymization:** Where possible, anonymize or pseudonymize personal data to reduce privacy risks. This is particularly crucial in datasets that may be publicly released or shared.

4. **Security by Design:** Integrate data protection features from the earliest stages of development. This includes implementing robust encryption, access controls, and secure data storage practices.

5. **Access Control:** Limit access to personal data to only those components or personnel who strictly need it for processing. Implement appropriate authentication and authorization mechanisms.

6. **Data Portability:** Facilitate easy extraction and transfer of data in a common format, allowing users to move their data between different services seamlessly.

7. **User Rights:** Respect user rights such as the right to access their data, the right to rectify inaccuracies, and the right to erasure (‘right to be forgotten’).

8. **Regular Audits and Updates:** Regularly review and update the software to address emerging security vulnerabilities and ensure compliance with evolving data protection laws.

9. **Documentation and Compliance:** Document data flows and privacy measures. While the software itself may not be directly subject to GDPR, good documentation practices help downstream users to achieve compliance.

10. **Community Awareness:** Encourage a culture of privacy awareness and compliance within the community. Contributors should stay informed about data protection best practices and legal requirements.

Remember, adhering to these guidelines not only helps in compliance with regulations like the GDPR but also builds trust with users and the broader community. As contributors, your commitment to these principles is invaluable in fostering a responsible and privacy-conscious software ecosystem.
