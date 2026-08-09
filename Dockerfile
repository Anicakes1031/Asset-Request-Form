FROM odoo:17.0

# Kopyahin ang custom app mo papunta sa Odoo extra-addons folder
COPY . /mnt/extra-addons/asset_form

# I-initialize ang Odoo database at i-install ang base + custom module mo
CMD ["odoo", "-d", "asset_request_form", "-i", "base,asset_form"]