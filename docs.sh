# Generating API docs
python manage.py generateschema --urlconf inventory.urls --title "Organization.supply REST API" > docs/api.yml
cp docs/api.yml hugo/content/api.yml # Also copy it to the static site content folder 

# Generating static site
cd hugo && hugo --destination ../docs --minify