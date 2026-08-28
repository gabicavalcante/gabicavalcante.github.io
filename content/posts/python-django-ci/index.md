+++
title = "Python, Django and GitHub CI"
description = "Continuous integration for a Django project with GitHub Actions: workflow triggers, environment variables, and running the suite with pytest."
date = "2019-09-30"
tags = ["python", "django", "ci-cd"]
+++

GitHub Actions was introduced last year, and it’s an API for cause and effect on GitHub. You can orchestrate any workflow, based on any event, you can have your workflow run on push events to master and release branches, or only run on `pull_request` events that target the master branch, or run every day of the week at Friday 02:00. The workflows are code in a repository, as you will see in this project, so you can create, share, reuse, and fork.

<!--more-->

I’m working in a Django project and when I started I found a problem: there was no CI/CD working or integration/unit test. In the past I used the GitLab CI/CD, but now the code was hosted on GitHub. So, my challenge was create tests to my Django project (it was implemented before I got the job) and create CI/CD pipeline for integrating it with GitHub CI/CD. For this tutorial, the application that I’m gonna show you, demonstrates CRUD operations using class based views in Django (you can find here). It also includes UI for all CRUD views and it’s based on the semaphoreci.com tutorial.

- Local project setup

```bash
$ virtualenv -p python3 env
```

- Download the project

```bash
$ git clone https://github.com/gabicavalcante/django-test-ci.git
```

- Install pip requirements

```bash
$ pip install -r requirements.txt
```

- Create a new psql database

```sql
postgres=# create database pydjango;
```

Setup your database credentials and `SITE_URL` in `settings.py` file available inside core folder.

Once you have setup your database, open command prompt and run the migrate command to create the application default database and the superuser.

```bash
(env) $ python manage.py migrate
(env) $ python manage.py createsuperuser
```

After all of the above command run successfully, let’s run:

```bash
(env) $ python manage.py runserver
```

And visit the web browser with http://127.0.0.1:8000

# Environment variables

The following environment variables can be set to override defaults:

- `SECRET_KEY`: Django secret key.
- `DB_ENGINE`: Django database backend.
- `DB_NAME`: database name.
- `DB_HOST`: database hostname.
- `DB_PORT`: database port.
- `DB_USER`: database user.
- `DB_PASSWORD`: database password.

# Test with PyTest

To tell `pytest` which Django settings that should be used for tests runs, we need to setup a `pytest` configuration file, called `pytest.ini` in our project root directory. The file contains:

```ini
[pytest]
DJANGO_SETTINGS_MODULE=core.test_settings
addopts = --nomigrations --cov=. --cov-report=html
```

To run the tests, we can invoke directly `pytest` command instead of `manage.py test`. The pytest-django is designed to run with the pytest command, but in case of you want to use `manage.py test` with pytest-django, you can create [a simple test runner](https://pytest-django.readthedocs.io/en/latest/faq.html#how-can-i-use-manage-py-test-with-pytest-django).
