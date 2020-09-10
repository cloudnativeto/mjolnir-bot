# -*- coding: utf-8 -*-
############################################################################
#  Copyright  2020  cloudnative.to open source team , @stevensu1977
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
############################################################################

import os
import collections
import hmac
import hashlib

from flask import request, jsonify

class Webhook(object):
    """
    Webhook构造器可以使用flask app 进行初始化.
    :param app: flask app对象负责底层的web通信实现
    :param endpoint: 提供给github调用的路径,默认为/payload
    """

    def __init__(self, app=None, endpoint="/payload"):
        self.app = app
        if app is not None:
            self._event_handlers = collections.defaultdict(list)
            app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=self.payload, methods=["POST"])
        else:
            raise Exception('need flask app')

    
    def verify_hmac_hash(self,data, signature):
        """
        verify_hmac_hash 通过github secret 计算payload内容是否正确
        """
        github_secret = bytes(os.environ['GITHUB_SECRET'], 'UTF-8')
        mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
        return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)
        

    def hook(self, event_type="push",action=None):
        """
        hook是一个修饰器,将被修饰的fuc注册到 self._event_handlers.
        :param event_type: event_type为需要修饰的fuc为github发送过来X-GitHub-Event的回调方法.
        :param action: 如果设置了action,那么会根据event的action判断是否需要处理,默认是处理改event下所有action
        """

        def decorator(func):
            print(func.__name__)
            def wrapped_f(*args):
                payload=args[0]
                if action is not None:
                    if payload['action']==action:
                        func(*args)
                else:
                    func(*args)

            self._event_handlers[event_type].append(wrapped_f)
            return wrapped_f

        return decorator

    def payload(self):
        """
        payload 默认的dispatch方法,会从该方法调用到各个event的回调方法
        """
        signature = request.headers.get('X-Hub-Signature')
        data = request.data
        if self.verify_hmac_hash(data, signature):
            event_type = request.headers.get('X-GitHub-Event')
            if event_type is None:
                return jsonify({'msg': "Bad Request"}),400
            handlers = self._event_handlers.get(event_type, [])
            if len(handlers)==0:
                return jsonify({'event': event_type,'msg':'missing event hooks'})
            for handler in handlers:
                handler(request.get_json())
            return jsonify({'event': event_type})
        else:
            return jsonify({'msg': 'invalid hash'}),400
