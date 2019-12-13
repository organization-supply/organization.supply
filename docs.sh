# Generating API docs
python manage.py generateschema --urlconf inventory.urls --title "Organization.supply REST API" > docs/api.yml
cp docs/api.yml hugo/content/api.yml

# Generating static site
cd hugo && hugo --destination ../docs --minify