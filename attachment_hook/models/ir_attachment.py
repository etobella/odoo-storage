# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _file_read_storage(self, fname, bin_size=False, **kwargs):
        return self._file_read(fname, bin_size=bin_size)

    @api.model
    def _file_write_storage(self, value, checksum, **kwargs):
        return {
            'store_fname': self._file_write(value, checksum),
        }

    @api.model
    def _file_delete_storage(self, fname, **kwargs):
        return self._file_delete(fname)

    def _search_file_storage(self):
        return bool(self.store_fname)

    def _file_storage_arguments(self):
        return {}
