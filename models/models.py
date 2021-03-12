# -*- coding: utf-8 -*-

from odoo import models, fields, api
#

class ResUser(models.Model):
    _inherit = 'res.users'
    _description = 'users'

    
    token = fields.Char(string='Token')
    url = fields.Char(string='URL')
    port = fields.Char(string='Port')

class Timesheet(models.Model):
    _name = 'timesheet'
    _description = 'attendance'

    
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
    )

    description = fields.Char(string='Description')
    project = fields.Char(string='Project')
    task = fields.Char(string='Task')
    log = fields.Char(string='Log')

    date_time = fields.Datetime(
        string='Date Time',
        default=fields.Datetime.now,
    )
    
    duration = fields.Float(string='Duration (Hours)', compute="_compute_time")
    
    in_id = fields.Many2one(
        string='IN',
        comodel_name='timesheet',
        ondelete='restrict',
    )
    

    def _compute_time(self):
        if self.in_id:
            pass
    
    
    
