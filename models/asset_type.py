from odoo import fields, models, api

class AssetType(models.Model):
    _name = 'asset.type'
    _description = 'asset type'

    name = fields.Char(string='Asset Type', required=True)


class AssetModel(models.Model):
    _name = 'asset.model'
    _description = 'asset model'
    _rec_name = 'display_name' 

    brand = fields.Char(string='Brand', required=True)
    name = fields.Char(string='Model Name', required=True)
    specification = fields.Char(string='Specification')
    asset_type_id = fields.Many2one('asset.type', string='Asset Type', required=True)
    
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    @api.depends('brand', 'name', 'specification')
    def _compute_display_name(self):
        for record in self:
            display_name = record.brand or ''

            if record.name:
                display_name += f" {record.name}"

            if record.specification:
                display_name += f" - {record.specification}"

            record.display_name = display_name