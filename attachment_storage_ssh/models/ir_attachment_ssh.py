# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError
import logging
import base64
_logger = logging.getLogger(__name__)
try:
    from paramiko.client import SSHClient
except (ImportError, IOError) as err:
    _logger.info(err)


class IrAttachmentSsh(models.AbstractModel):
    _name = 'ir.attachment.ssh'
    _inherit = 'ir.attachment.system'

    @api.model
    def ssh_connection(self, storage):
        connection = SSHClient()
        connection.load_system_host_keys()
        vals = storage.config
        connection.connect(
            hostname=vals.get('hostname', None),
            port=vals.get('port', 0),
            username=vals.get('user', None),
            password=vals.get('password', None)
        )
        sftp = connection.open_sftp()
        return connection, sftp

    @api.model
    def read_datas(self, fname, bin_size=False, storage_id=False, **kwargs):
        if not storage_id:
            raise UserError(_('Storage is required'))
        connection, sftp = self.ssh_connection(storage_id)
        sftp.normalize('.')
        sftp.chdir(storage_id.config.get('path', '.'))
        path = fname.split('/')
        file_name = path[-1]
        for p in path[:-1]:
            if p == "":
                continue
            try:
                sftp.chdir(p)
            except IOError:
                sftp.mkdir(p)
                sftp.chdir(p)
        f = sftp.open(file_name, 'rb')
        data = f.read()
        f.flush()
        f.close()
        sftp.close()
        connection.close()
        return base64.b64encode(data)

    @api.model
    def _compute_fname(self, value, checksum, storage_id=False, **kwargs):
        return checksum[:3] + '/' + checksum

    @api.model
    def write_datas(self, value, checksum, storage_id=False, **kwargs):
        if not storage_id:
            raise UserError(_('Storage is required'))
        connection, sftp = self.ssh_connection(storage_id)
        sftp.normalize('.')
        sftp.chdir(storage_id.config.get('path', '.'))
        bin_data = base64.b64decode(value) if value else b''
        fname = kwargs.get('fname', False)
        if not fname:
            fname = self._compute_fname(
                value, checksum, storage_id=storage_id, **kwargs)
        path = fname.split('/')
        file_name = path[-1]
        for p in path[:-1]:
            if p == "":
                continue
            try:
                sftp.chdir(p)
            except IOError:
                sftp.mkdir(p)
                sftp.chdir(p)
        f = sftp.open(file_name, 'wb')
        f.write(bin_data)
        f.flush()
        f.close()
        sftp.close()
        connection.close()
        return {'store_fname': fname}

    def delete_datas(self, fname, storage_id=False, **kwargs):
        if not storage_id:
            raise UserError(_('Storage is required'))
        connection, sftp = self.ssh_connection(storage_id)
        # path = sftp.normalize('.')
        sftp.close()
        connection.close()
