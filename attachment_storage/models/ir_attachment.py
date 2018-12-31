# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    storage_id = fields.Many2one(
        'ir.attachment.storage',
    )
    
    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        for attach in self.filtered(lambda r: r.storage_id):
            attach.datas = self.env[attach.storage_id.model].read_datas(attach)
        super(IrAttachment, self.filtered(
            lambda r: not r.storage_id))._compute_datas()

    def _inverse_datas(self):
        for attach in self.filtered(lambda r: r.storage_id):
           self.env[attach.storage_id.model].write_datas(attach)
        super(IrAttachment, self.filtered(
            lambda r: not r.storage_id))._inverse_datas()

    # TODO: Missing unlink
