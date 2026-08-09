FROM odoo:17.0

# Kopyahin ang custom app mo papunta sa Odoo extra-addons folder
COPY . /mnt/extra-addons/asset_form