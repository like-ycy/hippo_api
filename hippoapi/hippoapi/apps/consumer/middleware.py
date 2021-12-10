class AuthMiddleware:
    def __init__(self, application):  # 在用户请求进入路由分发之前自动执行，项目刚启动
        self.application = application
        print('AuthMiddleware>>>>>>', self.application)
        print(self)

    def __call__(self, scope):  # 每一次客户端请求都会经过这里。可以用户验证用户的权限
        print('AuthMiddleware>>>>>>call方法执行了', scope)
        # scope中封装了本次请求的所有信息
        return self.application(scope)
