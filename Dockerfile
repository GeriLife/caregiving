FROM python:3.9
LABEL maintainer="brylie@amble.fi"

ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev

RUN pip install --upgrade pip

# We use gunicorn to serve the project
RUN pip install gunicorn

# Poetry is used to manage dependencies
RUN pip install poetry

WORKDIR /app/
COPY /project/* /app/
COPY pyproject.toml /app/
COPY poetry.lock /app/

# Note: we don't want Poetry to create a virtual environment
# Instead, it should use a local directory
RUN poetry config virtualenvs.create false

# Install Poetry dependencies
RUN poetry install --no-dev

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

RUN useradd wagtail
RUN chown -R wagtail /app

USER wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Run the server
CMD set -xe; gunicorn --worker-tmp-dir /dev/shm core.wsgi:application --workers 3