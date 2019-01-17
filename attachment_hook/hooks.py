from odoo.addons.base.ir.ir_attachment import IrAttachment
import base64


def post_load_hook():

    if not hasattr(IrAttachment, 'old_compute_datas'):
        IrAttachment.old_compute_datas = IrAttachment._compute_datas

    if not hasattr(IrAttachment, 'old_inverse_datas'):
        IrAttachment.old_inverse_datas = IrAttachment._inverse_datas

    if not hasattr(IrAttachment, 'old_unlink'):
        IrAttachment.old_unlink = IrAttachment.unlink

    def _new_compute_datas(self):
        if not hasattr(self, '_file_read_storage'):
            return self.old_compute_datas()
        bin_size = self._context.get('bin_size')
        for attach in self:
            if attach._search_file_storage():
                attach.datas = self._file_read_storage(
                    attach.store_fname, bin_size,
                    **(attach._file_storage_arguments()))
            else:
                attach.datas = attach.db_datas

    def _new_inverse_datas(self):
        if not hasattr(self, '_file_read_storage'):
            return self.old_inverse_datas()
        location = self._storage()
        for attach in self:
            # compute the fields that depend on datas
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname,
                                             attach.mimetype),
                'store_fname': False,
                'db_datas': value,
            }
            if value and location != 'db':
                # save it to the filestore
                vals.update(self._file_write_storage(
                    value, vals['checksum'],
                    **(attach._file_storage_arguments())
                ))
                vals['db_datas'] = False

            # take current location in filestore to possibly garbage-collect it
            fname = attach.store_fname
            # write as superuser, as user probably does not have write access
            super(IrAttachment, attach.sudo()).write(vals)
            if fname:
                self._file_delete_storage(
                    fname, **(attach._file_storage_arguments()))

    def new_unlink(self):
        if not hasattr(self, '_file_read_storage'):
            return self.old_unlink()
        self.check('unlink')

        # First delete in the database, *then* in the filesystem if the
        # database allowed it. Helps avoid errors when concurrent transactions
        # are deleting the same file, and some of the transactions are
        # rolled back by PostgreSQL (due to concurrent updates detection).
        to_delete = [(
            attach.store_fname, attach._file_storage_arguments()
        ) for attach in self if attach._search_file_storage()]
        res = super(IrAttachment, self).unlink()
        for file_path, args in to_delete:
            self._file_delete_storage(file_path, **args)
        return res

    IrAttachment.unlink = new_unlink
    IrAttachment._compute_datas = _new_compute_datas
    IrAttachment._inverse_datas = _new_inverse_datas
