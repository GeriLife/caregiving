# Deployment

This section is a work-in-progress and outlines issues that arise during or relate to deployment. The main assumption is that we are deploying to [Dokku PaaS](https://dokku.com).

## Configure initial app and domain

Configure the initial Dokku app and database with the following commands.

- create app `dokku apps:create caregiving-app`
- configure app domain `sudo dokku domains:add caregiving-app <example.com>`
- set `DJANGO_ALLOWED_HOSTS` to include app domain `dokku config:set caregiving-app DJANGO_ALLOWED_HOSTS=<example.com>`
- set `DJANGO_CSRF_TRUSTED_ORIGINS` to include app domain with scheme (e.g., https://) `dokku config:set caregiving-app DJANGO_CSRF_TRUSTED_ORIGINS=<https://example.com>`

## Set up SSL

Enable HTTPS support with the following commands on the Dokku server.

- install Let's Encrypt `dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git`
- configure Let's Encrypt email `dokku config:set --no-restart --global DOKKU_LETSENCRYPT_EMAIL=<user@email.com>`
- enable Let's Encrypt for app `dokku letsencrypt:enable caregiving-app`
- auto-update Let's Encrypt certificate `dokku letsencrypt:cron-job --add`'
  - `dokku letsencrypt:auto-renew caregiving-app`

## Set up database

- install Postgres plugin `dokku plugin:install https://github.com/dokku/dokku-postgres.git`
- create Postgres DB `dokku postgres:create caregiving-db`
- link DB to app `dokku postgres:link caregiving-db caregiving-app`

## Push code from local computer

Now that the Dokku app and database are configured, push code from a local computer to the Dokku server.

- add Git remote on local computer `git remote add dokku dokku@<dokku_server>:caregiving-app`
- push changes to `dokku` remote `git push dokku main:main`

## Enter the Dokku app

The following commands will need to be run from within the Dokku app. Use the following command on the Dokku server to enter the app.

- `dokku enter caregiving-app`

### Run database migrations

For now, database migrations need to be run manually, until a post deployment task is configured. Run the database migrations with the following command.

- `python manage.py migrate`

### Create initial Django superuser

Create an initial superuser on the deployed app with the following command.

- `python manage.py createsuperuser`

Follow the prompts to create the initial superuser.
