
# Migrate first
python manage.py makemigrations
python manage.py migrate

# Collect static
python manage.py collectstatic --noinput

# Then start server
port=${1:-80}
/usr/local/bin/gunicorn inventory.wsgi:application -w 2 -b :${port} --reload --enable-stdio-inheritance
