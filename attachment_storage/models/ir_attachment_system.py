# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachmentSystem(models.AbstractModel):
    _name = 'ir.attachment.system'
    _description = 'Ir Attachment System'

    @api.model
    def read_datas(self, fname, bin_size=False, **kwargs):
        pass

    @api.model
    def write_datas(self, value, checksum, **kwargs):
        pass

    @api.model
    def delete_datas(self, fname, **kwargs):
        pass
