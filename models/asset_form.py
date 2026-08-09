from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.osv import expression
import base64

class AssetForm(models.Model):
    _name = 'asset.form'
    _description = "Asset Form fields"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    asset_reference = fields.Char(string='Asset Reference No.', readonly=True, default='AR-0000', copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    model_id = fields.Many2one('asset.model', string='Model', required=True)
    serial_number = fields.Char(string='Serial Number')
    asset_type_id = fields.Many2one('asset.type', string='Asset Type', required=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True, readonly=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('it_approved', 'IT Approved'),
        ('ceo_approved', 'CEO Approved'),
        ('treasury', 'For Purchase'),
        ('released', 'Released'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    date = fields.Datetime(string='Date', readonly=True, default=fields.Datetime.now)


    it_signature = fields.Binary(string='IT Signature', attachment=True)
    it_signature_name = fields.Char(string='IT Signatory Name')
    
    ceo_signature = fields.Binary(string='CEO Signature', attachment=True)
    ceo_signature_name = fields.Char(string='CEO Signatory Name')
    
    treasury_signature = fields.Binary(string='Treasury Signature', attachment=True)
    treasury_signature_name = fields.Char(string='Treasury Signatory Name')

    it_signed = fields.Boolean(string='IT Signed', compute='_compute_signature_status')
    ceo_signed = fields.Boolean(string='CEO Signed', compute='_compute_signature_status')
    treasury_signed = fields.Boolean(string='Treasury Signed', compute='_compute_signature_status')

    def _is_employee_user(self):
        return self.env.user.has_group('base.group_user') and not (
            self._is_it_department() or self._is_ceo() or self._is_treasury() or self._is_admin()
        )

    def _get_visibility_domain(self):
        if self._is_admin() or self._is_it_department() or self._is_ceo() or self._is_treasury():
            return []
        if self._is_employee_user():
            return [('employee_id.user_id', '=', self.env.user.id)]
        return []

    @api.model
    def _search(self, domain, *args, **kwargs):
        visibility_domain = self._get_visibility_domain()
        if visibility_domain:
            domain = expression.AND([domain, visibility_domain])
        return super()._search(domain, *args, **kwargs)

    @api.onchange('it_signature_name')
    def _onchange_it_signature_name(self):
        if self.it_signature_name:
            self.it_signature_name = self.it_signature_name.upper()

    @api.onchange('ceo_signature_name')
    def _onchange_ceo_signature_name(self):
        if self.ceo_signature_name:
            self.ceo_signature_name = self.ceo_signature_name.upper()

    @api.onchange('treasury_signature_name')
    def _onchange_treasury_signature_name(self):
        if self.treasury_signature_name:
            self.treasury_signature_name = self.treasury_signature_name.upper()

    @api.depends('it_signature', 'ceo_signature', 'treasury_signature')
    def _compute_signature_status(self):
        for record in self:
            record.it_signed = bool(record.it_signature)
            record.ceo_signed = bool(record.ceo_signature)
            record.treasury_signed = bool(record.treasury_signature)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['asset_reference'] = self.env['ir.sequence'].next_by_code(
                'asset.form'
            ) or 'New'
        return super().create(vals_list)
    
    def _is_it_department(self):
        return self.env.user.has_group('asset_form.group_it_department') or self.env.user.has_group('base.group_system')
    
    def _is_ceo(self):
        return self.env.user.has_group('asset_form.group_ceo') or self.env.user.has_group('base.group_system')
    
    def _is_treasury(self):
        return self.env.user.has_group('asset_form.group_treasury') or self.env.user.has_group('base.group_system')
    
    def _is_admin(self):
        return self.env.user.has_group('base.group_system')

    def action_set_it_approved(self):
        for record in self:
            if record.status != 'draft':
                raise ValidationError("Only Draft records can be IT Approved.")
            
            if not record.it_signature:
                raise ValidationError("Please upload IT signature before approving.")
            
            record.status = 'it_approved'

    def action_set_ceo_approved(self):
        for record in self:
            if record.status != 'it_approved':
                raise ValidationError("Only IT Approved records can be CEO Approved.")
            
            if not record.ceo_signature:
                raise ValidationError("Please upload CEO signature before approving.")
            
            record.status = 'ceo_approved'

    def action_set_treasury(self):
        for record in self:
            if record.status != 'ceo_approved':
                raise ValidationError("Only CEO Approved records can be sent to Treasury.")
            
            if not record.treasury_signature:
                raise ValidationError("Please upload Treasury signature before processing.")
            
            record.status = 'treasury'

    def action_set_released(self):
        for record in self:
            if record.status != 'treasury':
                raise ValidationError("Only Treasury records can be Released.")
            if not record.serial_number:
                raise ValidationError("Please provide Serial Number before releasing.")
            record.status = 'released'

    def action_cancel(self):
        for record in self:
            if record.status == 'released':
                raise ValidationError("Cannot cancel a Released record.")
            if record.status == 'cancelled':
                raise ValidationError("Record is already cancelled.")
            record.status = 'cancelled'

    def action_print_report(self):
        """Print the asset request report"""
        return self.env.ref('asset_form.action_asset_form_report').report_action(self)
    
class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        user = super().create(vals)
        if not self.env.user.has_group('base.group_system'):
            internal_user_group = self.env.ref('base.group_user')
            user.groups_id = [(6, 0, [internal_user_group.id])]
        return user