# -*- coding: utf-8 -*-
from pathlib import Path  # Python 3.6+ only
from odoo import http

from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception

import json
import string
import random

import face_recognition as fr
import io
import base64
import numpy as np

import os

# .env
from dotenv import load_dotenv
load_dotenv()

import jwt


def get_face_encoding_from_base64(base64String):
    image = fr.load_image_file(io.BytesIO(base64.b64decode(base64String)))
    image_encoding = fr.face_encodings(image)[0]
    return image_encoding

class Users(http.Controller):
    @http.route('/api/login', auth='none', type='http', methods=['POST'], csrf=False)
    @serialize_exception
    def Login(self, **kw):
        """ email, password """
        response = {}
        if 'email' in kw and 'password' in kw:
            session = request.session
            try:
                login = request.session.authenticate(
                    session['db'], kw['email'], kw['password']
                )
            except:
                response['status'] = 'denied'
                return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

            user = request.env['res.users'].sudo().search([('login', '=', kw['email']), ('active', '=', True)], limit=1)
            secret = os.environ.get("secret")
            token = jwt.encode({"id": user.id}, secret, algorithm="HS256")
            response = {
                "name": user['name'] or "",
                "email": user['login'] or "",
                "token": token,
                "hasPic": True if user['image_1920'] else False
            }            
            return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])
        else:
            response['status'] = 'error'
            return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])


class Timesheet(http.Controller):
    @http.route('/api/attendance', auth='none', type='http', methods=['POST'], csrf=False)
    def Attendance(self, **kw):
        """ Timesheet """
        response = {}
        secret = os.environ.get("secret")
        token = jwt.decode(kw['token'], secret, algorithms=["HS256"])
        user = request.env['res.users'].sudo().browse(int(token['id']))
        if user:
            try:
                image_receive = get_face_encoding_from_base64(kw['image'])
            except:
                response['status'] = 'not-clear'
                return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])
            user_img = get_face_encoding_from_base64(user.image_1920)
            result = fr.compare_faces([user_img], image_receive)
            if True in result:
                response['status'] = 'success'
            else:
                response['status'] = 'not-clear'
            return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])
        response['status'] = 'error'
        return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])



    @http.route('/api/attendance/info', auth='none', type='http', methods=['POST'], csrf=False)
    def AttendanceInfo(self, **kw):
        response = {}
        secret = os.environ.get("secret")
        token = jwt.decode(kw['token'], secret, algorithms=["HS256"])
        user = request.env['res.users'].sudo().browse(int(token['id']))
        if user:
            if kw['type'] == 'Time-In':
                attendance = request.env['timesheet'].with_user(user.id).create({
                    'log': 'In',
                    'description': kw['description'] if 'description' in kw else "",
                    'project': kw['project'] if 'project' in kw else "",
                    'task': kw['task'] if 'task' in kw else "",
                })
            else:
                attendance = request.env['timesheet'].with_user(user.id).create({
                    'log': 'Out',
                    'description': kw['description'] if 'description' in kw else "",
                    'project': kw['project'] if 'project' in kw else "",
                    'task': kw['task'] if 'task' in kw else "",
                    # 'in_id': [4()] # todo
                })
        response['status'] = 'error' if not attendance else 'success'
        return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

    @http.route('/api/attendance/info/get', auth='none', type='http', methods=['GET'], csrf=False)
    def AttendanceGetInfo(self, **kw):
        response = {
            "timesheet": []
        }
        secret = os.environ.get("secret")
        print(type(kw))
        # json.loads(kw)
        token = jwt.decode(kw['token'], secret, algorithms=["HS256"])
        user = request.env['res.users'].sudo().browse(int(token['id']))
        if user:
            timesheets = request.env['timesheet'].with_user(user.id).search([('create_uid', '=', user.id)])
            for timesheet in timesheets:
                print(timesheet.date)
                response['timesheet'].append({
                    "id": timesheet.id,
                    "date": str(timesheet.date),
                    "project": timesheet.project,
                    "task": timesheet.task,
                    "description": timesheet.description
                })
            print(response)
            return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])
        response['status'] = 'error'
        return request.make_response(json.dumps(response), [('Access-Control-Allow-Origin', '*')])

# for testing
class Index(http.Controller):
    @http.route('/index', auth='none', type='http', methods=['GET'], csrf=False)
    def index(self, **kw):
        print('Hello World', os.environ.get("api-token"))
        secret = os.environ.get("secret")
        encoded_jwt = jwt.encode({"some": "payload"}, secret, algorithm="HS256")
        # print(encoded_jwt)
        print(jwt.decode(encoded_jwt, secret, algorithms=["HS256"]))
        
        print(request.env['timesheet'].with_user(2).search([('create_uid', '=', 6)]))
        return "Hello, World"

