# -*- coding: UTF-8 -*-
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class Authentication(MiddlewareMixin):

    def process_request(self, request):
        # 0.排除那些不需要登录就能访问的页面
        #   request.path_info 获取当前用户请求的URL /login/
        if request.path_info in ["/", "/user_img/", "/login/", "/register/"]:
            return

        # 1.读取当前访问的用户的session信息，如果能读到，说明已登陆过，就可以继续向后走。
        step = request.session.get("step")
        if step is not None:
            if step >= 5:
                return
            elif request.path_info in ["/area2/", "/area3/", "/area4/", "/polling/", "/bug_detail/",
                                       "/dynamic_bug_detail/", "/pause_detection/", "/continue_detection/"]:
                return JsonResponse({"status": "not started"})
            elif request.path_info in ["/area1/"] and step < 4:
                return JsonResponse({"status": "not generated"})
            elif request.path_info in ["/generate/"] and step < 3:
                return JsonResponse({"status": "not uploaded"})
            elif request.path_info in ["/upload/"] and step < 2:
                return JsonResponse({"status": "not connected"})
            else:
                return
        else:
            # 2.没有登录过，重新回到登录页面
            return JsonResponse({"status": "not login"})
