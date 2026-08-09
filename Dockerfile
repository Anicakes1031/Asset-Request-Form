FROM odoo:17.0

COPY . /mnt/extra-addons/asset_form

# Explicitly set the Postgres DB port to 5432
CMD ["odoo", "--db_port=5432"]