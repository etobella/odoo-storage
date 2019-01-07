# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    storage_id = fields.Many2one(
        'ir.attachment.storage',
    )

    @api.model
    def _file_read_storage(self, fname, bin_size=False, **kwargs):
        if kwargs.get('storage_id', False):
            return self.env[kwargs['storage_id'].model].read_datas(
                fname, bin_size=False, **kwargs
            )
        return super()._file_read_storage(fname, bin_size=bin_size, **kwargs)

    @api.model
    def _file_write_storage(self, value, checksum, **kwargs):
        if kwargs.get('storage_id', False):
            return self.env[kwargs['storage_id'].model].write_datas(
                value, checksum, **kwargs
            )
        return super()._file_write_storage(value, checksum, **kwargs)

    @api.model
    def _file_delete_storage(self, fname, **kwargs):
        if kwargs.get('storage_id', False):
            return self.env[kwargs['storage_id'].model].delete_datas(
                fname, **kwargs
            )
        return super()._file_delete_storage(fname, **kwargs)

    def _search_file_storage(self):
        return self.storage_id or bool(self.store_fname)

    def _file_storage_arguments(self):
        return {'storage_id': self.storage_id}
