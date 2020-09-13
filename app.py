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
import hmac
import hashlib

import sys

from flask import Flask, jsonify
from github import Github

import webhook

import aws_lambda_wsgi

#检查环境变量是否有GITHUB_ACCESS_TOKEN和GITHUB_SECRET
if os.environ.get('GITHUB_ACCESS_TOKEN') is None :
    print('missing GITHUB_ACCESS_TOKEN ')
    sys.exit(-1)

if os.environ.get('GITHUB_SECRET') is None :
    print('missing GITHUB_SECRET')
    sys.exit(-1)


WELCOME_MSG="""Hello, I am @mjolnir-bot. I am here to help you get the issue triaged.

It looks like you have not filled out the issue in the format of any of our templates. To best assist you, we advise you to use one of these [templates](https://github.com/cloudnativeto).

I have CC'd a few people who may be able to assist you:
* @stevensu1977 (found keywords: join)

If we have not gotten back to your issue within a few business days, you can try the following:
* Join our [community slack channel](https://github.com/cloudnativeto/community/slack) and ask on #cloudnativeto.
* Try find someone from [here](https://github.com/orgs/cloudnativeto/people) if you know they worked closely on the area and CC them.

<sub>:owl: Hoot! I am a [Mjölnir-Bot], a bot for [cloudnativeto](https://github.com/cloudnativeto). My owner is [stevensu1977](https://github.com/stevensu1977).</sub>

_Originally posted by @mjolnir-bot in https://github.com/cloudnativeto"""


#初始化PyGithub    
github = Github(os.environ.get('GITHUB_ACCESS_TOKEN'))


app = Flask(__name__)

hook = webhook.Webhook(app)
app.logger.debug("Load GITHUB_SECRET,GITHUB_ACCESS_TOKEN successful")



def get_repo(repo_name):
    return  github.get_repo(repo_name)

def verify_hmac_hash(data, signature):
    """
    verify_hmac_hash 通过github webhook secret 计算msg内容是否正确
    """
    github_secret = bytes(os.environ['GITHUB_SECRET'], 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)



@hook.hook(event_type="issues",action="opened")        
# 为issues/opened事件,定义一个回调方法
def on_issues_opened(payload):
    print("Got issues opened event with: {0}".format(payload["issue"]["number"]))
    repo = get_repo(payload["repository"]["full_name"])
    issue = repo.get_issue(payload["issue"]["number"])
    exit_label=False
    issue.create_comment(WELCOME_MSG)
    for label in issue.labels:
        if label.name =="status/wait-answer":
            exit_label=True
    if exit_label == False:
        issue.add_to_labels("status/wait-answer")

@hook.hook(event_type="issue_comment",action="created")        
# 为issue_comment/created事件,定义一个回调方法 
def on_issue_comment_created(payload):
    print("Got issue_comment created event with: {0}".format(payload["issue"]["number"]))
    repo = get_repo(payload["repository"]["full_name"])
    issue = repo.get_issue(payload["issue"]["number"])    
    print(payload["issue"]["number"],issue.comments)
    if "/resolved" in payload["comment"]["body"]:
        issue.add_to_labels("status/resolved")
    elif "/stared" in payload["comment"]["body"]:
        issue.add_to_labels("type/stared")
    elif "/faq" in payload["comment"]["body"]:
        issue.add_to_labels("type/faq")
    
    else:
        if payload["sender"]["login"]!="mjolnir-bot" and payload["sender"]["login"]!=issue.user.login:
            issue.add_to_labels("status/replied") 
            issue.remove_from_labels("status/wait-answer")


@app.route('/')
@app.route('/v1')
def hello_world():
    return jsonify({'zerobot': 'v0.0.1'})


def lambda_handler(event, context):
    #debug print(event)
    # bug: 如果使用API Gateway HTTP trigger lambda ,aws_lambda_wsgi 会报找不到httpMethod,path, queryStringParameters的KeyError
    # 暂时通过代码为API Gateway HTTP 增加httpMethod, path, queryStringParameters 三个环境参数
    elb = 'elb' in event['requestContext']
    if elb == False:
        event['httpMethod']=event['requestContext']['http']['method']
        event['path'] = event['requestContext']['http']['path']
        event['queryStringParameters']=''
    return aws_lambda_wsgi.response(app, event, context)

if __name__ == "__main__":
    #本地部署默认打开调试模式
    app.debug = True
    app.run(host="0.0.0.0")