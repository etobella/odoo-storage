# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachmentStorage(models.Model):
    _name = 'ir.attachment.storage'
    _description = 'Attachment Storage'  # TODO

    name = fields.Char(required=True)
    model = fields.Char(required=True)
    config = fields.Serialized(
        help="JSON containing all the information"
    )
