# [Organization.supply](https://organization.supply)

[![CircleCI](https://circleci.com/gh/jplattel/organization.supply.svg?style=svg)](https://circleci.com/gh/jplattel/organization.supply)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is a Django application that aspires to be a Saas startup, we currently use it for [our brewery](https://brouwerijnooitgedacht.nl). The primary goals is to have one simple interface to manage inventory. We build integrations as we require them. For example integration with financial parts or our webshop which runs woocommerce.

# Documentation & landing pages

Documentation and landing pages work with Github Pages. They are generated from the `hugo` folder into the docs folder with the `docs.sh` script. You will need [Hugo](https://gohugo.io/) installed for this to work.

# Development

It's a django app, so you will need python and other things installed (all in requirements.txt). Once installed run `python manage.py runserver` for local development. Code is formatted by `black`. Which you can run easily after installing with `black .`.

Errors are tracked with Sentry. This is configured trough the .env file in which you will need to fill in the SENTRY_DSN variable. A `.env.example` file is provided.

A `docker-compose.yml` file is also available for this stack for development. It runs the application with a Postgres DB instead of a sqlite one. A simple `build` and `up` should be enough, you can create a superuser in the python application container. Since it's storing data, you might need to create a volume with: `docker volume create --name=inventory`.

# Testing

Testing is done with pytest: `pytest`. If you want the coverage reports, run `pytest --cov-report html .` and look in the `tests/reports` directory to see the HTML output. The aim is to keep the coverage as high as possible.

# Deployment

Deployment is done manually for now, on a Digital Ocean droplet.

# License

[GNU Affero General Public License v3.0](https://choosealicense.com/licenses/agpl-3.0/)