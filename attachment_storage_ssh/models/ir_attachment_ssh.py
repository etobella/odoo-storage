# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import logging
import base64
_logger = logging.getLogger(__name__)
try:
    from paramiko.client import SSHClient
except (ImportError, IOError) as err:
    logging.info(err)


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
    def read_datas(self, attach):
        connection, sftp = self.ssh_connection(attach.storage_id)
        sftp.normalize('.')
        sftp.chdir(attach.storage_id.config.get('path', '.'))
        fname = attach.store_fname
        path = fname.split('/')
        file_name = path[-1]
        for p in path[:-1]:
            _logger.info(p)
            if p == "":
                continue
            try:
                sftp.chdir(p)
            except IOError:
                _logger.info('Create folder %s' % p)
                sftp.mkdir(p)
                sftp.chdir(p)
        f = sftp.open(file_name, 'rb')
        data = f.read()
        f.flush()
        f.close()
        sftp.close()
        connection.close()
        _logger.info(data)
        return base64.b64encode(data)

    @api.model
    def write_datas(self, attach):
        connection, sftp = self.ssh_connection(attach.storage_id)
        sftp.normalize('.')
        sftp.chdir(attach.storage_id.config.get('path', '.'))
        value = attach.datas
        bin_data = base64.b64decode(value) if value else b''
        fname = attach.store_fname
        if not fname:
            today = fields.Date.from_string(fields.Date.today())
            fname = '%s/%s/%s/%s' % (
                today.year,
                today.month,
                today.day,
                attach.id
            )
        _logger.info(fname)
        vals = {
            'file_size': len(bin_data),
            'checksum': attach._compute_checksum(bin_data),
            'index_content': attach._index(bin_data, attach.datas_fname, attach.mimetype)
        }
        if not attach.store_fname:
            vals['store_fname'] = fname
        path = fname.split('/')
        file_name = path[-1]
        for p in path[:-1]:
            if p == "":
                continue
            try:
                sftp.chdir(p)
            except IOError:
                _logger.info('Create Path %s' % p)
                sftp.mkdir(p)
                sftp.chdir(p)
        f = sftp.open(file_name, 'wb')
        f.write(bin_data)
        f.flush()
        f.close()
        attach.sudo().write(vals)
        sftp.close()
        connection.close()

    def delete_datas(self, attach):
        connection, sftp = self.ssh_connection(attach.storage_id)
        path = sftp.normalize('.')
        sftp.close()
        connection.close()
