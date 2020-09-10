# mjolnir-bot
社区自动机器人， 妙尔尼尔（Mjölnir)，内测中,

测试repo ,  https://github.com/cloudnativeto/zerobot-test/issues

**技术选型**

* 语言: python 
* lib: flask, pygithub, aws_lambda_wsgi 

* 部署方式: 支持本地、公有云虚机部署、支持serverless函数式部署



**技术架构**

\- webhook.py 提供修饰器模式, 用于接收 Github HTTP 回调，触发各类事件处理

\- app.py 主程序, 各类环境、库初始化

```python
#扩通过修饰器,定义一个issues/opened的回调方法, 如果action不设置，则所有issues event都将回调该方法
webhook_handler = webhook.Webhook(app)
@webhook_handler.hook(event_type="issues",action="opened")        
# 为issues/opened事件,定义一个回调方法
def on_issues_opened(payload):
    print("Got issues opened event with: {0}".format(payload["issue"]["number"]))
    repo = get_repo(payload["repository"]["full_name"])
    issue = repo.get_issue(payload["issue"]["number"])
    exit_label=False
    issue.create_comment("welcome to cloudnative")
    for label in issue.labels:
        if label.name =="status/wait-answer":
            exit_label=True
    if exit_label == False:
        issue.add_to_labels("status/wait-answer")
```





**TODO**

\* 基本环境搭建, 本地,  AWS Lambda

\* Webhook event 测试

\* 逻辑处理



**功能**

\- 用户创建 Issue 后，自动为 Issue 添加 Label

​    \- 用户创建 Issue 后，自动添加 `status/wait-answer` 标签

​    \- 社区成员回答之后，自动添加 `status/replied` 标签

​    \- 问题解决后，自动添加 `status/resolved` 标签

​    \- 如果问题为精选 Issue，自动添加 `type/stared` 标签

​    \- 如果该文档被归档为 FAQ，自动添加 `type/faq` 标签

​    \- (其他)

\- 用户创建 Issue 后，自动回复 Issue，参考 [CockroachDB Issue](https://github.com/cockroachdb/cockroach/issues/53634#issuecomment-683320588)，需要包含以下内容：

​    \- 如何在社区寻找帮助

​    \- 如果是首次新建 Issue，可以指引如何加入社区

​    \- 如果不是 Organization 成员，可以引导加入 Github Organization（可以自动邀请）

​    \- 提示用户常用的 Issue 指令，例如：

​        \- `/join`  加入社区

​        \- `/label kubernetes` 给 Issue 添加 Label

​        \- `/faq` 将 Issue 归档为 FAQ

​        \- `/sig kubernetes` 可以邀请 Kubernetes SIG 的成员回答问题

​    \- 社区回答问题积分排行榜

\- 自动为 Issue 归档，生成 Issue 周报

\- 社区成员积分管理

​    \- 用户提出问题，可以添加悬赏（可以在 Issue 模板中包含一个悬赏积分的字段），问题解决之后，悬赏积分累计到回答问题的人用户账号之下

​    \- 所有用户都包含初始积分 500 分

​    \- 所有用户回答问题得到的积分，会实时计算累加并更新社区排行榜

​    \- 所有被标记为 `type/faq` 和 `type/stared` 的 Issue 将获得额外积分奖励

​    \- 所有积分公开透明，可以点击任意用户查看所有积分获得记录

​    \- 管理员有权使用 `/reward @lonng 100` 指令为用户新增积分

\- pull request

​    \- 自动 PR 合并
​    \- 积分管理
​    \- 自动添加标签







