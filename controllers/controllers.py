

import io
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import tempfile
import time
import zlib

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict
from werkzeug.urls import url_decode, iri_to_uri
from xml.etree import ElementTree
# import unicodedataimport odoo
import json
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_resource_path
from odoo.tools import crop_image, topological_sort, html_escape, pycompat
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlwt, file_open
from odoo.tools.safe_eval import safe_eval
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security







class Mobile_Functions(http.Controller):

    @http.route('/mobile/session/get_session_info', type='json', auth="user")
    def get_session_info(self):
        request.session.check_security()
        request.uid = request.session.uid
        request.disable_db = False
        return request.env['ir.http'].session_info()

    @http.route('/mobile/login', type='json', auth="user")
    def authenticate(self, db, login, password, base_location=None):
        session = request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()
    
    #registering to the application
    @http.route('/mobile/register', type='json', csrf=False, auth="public")
    def client_registration(self, name, email, password):
        data = request.env['res.users'].sudo().create({
            'name':name,
            'login':email,
            'new_password':password
        })
        if data:
            return "Successfully registered. Please login to Continue"
        else:
            return "there was a problem. Please try again"

    
    
    # displaying loans of a loggedin user
    @http.route('/mobile/loans', type='json', auth="user")
    def user_loan(self):
        loggedon = request.session.uid
        partner = request.env['res.users'].sudo().search([('id','=',loggedon)])
        loan = request.env['account.loan'].sudo().search([('partner_id','=',int(partner.partner_id))])
        if loan:
            result = []
            for i in loan:
                context = { "loan":i.name, "amount":i.loan_amt, "period":i.loan_period, "state":i.state}
                result.append(context)
            return result
        else:
            return "you have no loans yet"
        
        
    # creating loan application
    @http.route('/mobile/loan/create', type='json',csrf=False, auth="user")
    def create_loan(self, purpose, loan_period, state, amount, loan_type):
        id = request.session.uid
        user = request.env['res.users'].sudo().search([('id','=', id)])
        for i in user:
            borrower = int(i.partner_id)
            # checking if user has incomplete loans
            loans = request.env['account.loan'].sudo().search([('partner_id','=',borrower),('state', '!=','done')])
            if loans:
                return "you have another loan on progres. you can not create until current loan is completed"
            else:
                loan = request.env['account.loan'].sudo().create({ "name":purpose, "req_amount":amount, "loan_type":loan_type, "user_id": 2, "loan_period":loan_period, "state": state, "partner_id":borrower, "loan_amt":amount })  
            return loan
        
        
    # checking repayments statuses of installments
    @http.route('/mobile/loan/repayments', type='json', csrf=False, auth='user')
    def loan_repayments(self, loan_id):
        result = []
        repayment = request.env['account.loan.installment'].sudo().search([('loan_id','=',loan_id)])
        for i in repayment:
            inst = {
                'instalment name': i.name,
                'outstanding principle': i.outstanding_prin,
                'outstanding Interest': i.outstanding_int,
                'outstanding Fees': i.outstanding_fees,
                'State':i.state,
                'Date':i.date
            }
            result.append(inst)
        return result
    
    
    #checking the repayments schedules for a loan application
    @http.route('/mobile/loan/schedules', type='json', csrf=False, auth='user')
    def loan_schedules(self, loan_id):
        result = []
        schedule = request.env['payment.schedule.line'].sudo().search([('loan_id','=',loan_id)])
        
        for i in schedule:
            inst = {
                'instalment name': i.name,
                'principle': i.capital,
                'Interest': i.interest,
                'Fees': i.fees,
                'State':i.is_paid_installment,
                'Date':i.date
            }
            result.append(inst)
        return result
            
        
    
    
    
