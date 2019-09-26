# Inventory

This is a small Django application that provides our brewery an inventory tool. The primary goals is to have one simple interface to manage inventory with. And build integrations as our brewery requires. For example integration with financial parts or our webshop which runs woocommerce.

# Development

It's a django app, so you will need python and other things installed (all in requirements.txt). Once installed run `python manage.py runserver` for local development. Code is formatted by `black`. Which you can run easily after installing with `black .`.

Errors are tracked with Sentry. This is configured trough the .env file in which you will need to fill in the SENTRY_DSN variable. A `.env.example` file is provided.

# Testing

Testing is done with pytest: `pytest`. If you want the coverage reports, run `pytest --cov-report html .` and look in the `tests/reports` directory to see the HTML output. The aim is to keep the coverage as high as possible.


# Deployment

TBD.
