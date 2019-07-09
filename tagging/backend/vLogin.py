from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import models
import hashlib
import os
# Create your views here.
@csrf_exempt
def login(request):
    returnMessage = {}
    returnStatus = 200
    response = HttpResponse()
    try:
        if request.method == "POST":
            reqd = json.loads(request.body.decode("utf-8"))
            email = reqd['email']
            password = reqd['password']
            user = models.User.objects.get(email=email)
            if not user:
                returnMessage['detail']= "用户未注册"
                returnStatus = 401
            elif password == user.password:
                returnMessage['detail'] = "登录成功"
                # response = HttpResponse(json.dumps(returnMessage),returnStatus)
                # response.set_cookie('name',user.name)
                response.set_cookie('email',email)
                token = hashlib.sha1(os.urandom(24)).hexdigest()
                # token= "token"
                user.token = token
                user.save()
                response.set_cookie('token',token)
            else:
                returnMessage['detail'] = "密码错误"
                returnStatus = 401

    except Exception as ex:
        returnMessage['detail'] = str(ex)
        returnStatus = 401
    response.status_code = returnStatus
    response.content = json.dumps(returnMessage)
    return response

@csrf_exempt
def register(request):
    returnMessage = {}
    returnStatus = 401
    response = HttpResponse()
    if request.method == "POST":
        # req = json.loads(request.body.decode('utf-8'))
        # try:
            
        reqd = json.loads(request.body.decode('utf-8'))
        # reqd = (req)
        email = reqd['email']
        name = reqd['name']
        password = reqd['password']
        sameEmailUser = models.User.objects.filter(email = email)
        if sameEmailUser :
            returnMessage['detail'] = "此邮箱已经被注册"
            returnStatus = 401
        elif name and password and email:
            new_user = models.User(email = email,name = name,password = password)
            print(name)
            # response.set_cookie('name',name)
            response.set_cookie('email',email)
            token = hashlib.sha1(os.urandom(24)).hexdigest()
            # token= "token"
            new_user.token = token
            new_user.save()
            response.set_cookie('token',token)
            response.set_cookie('tag-count',0)
            returnMessage['detail']= "注册成功"
            returnStatus = 200
        else:
            returnMessage['detail'] = "表单内容有误"
        # except Exception as ex:
        #     returnMessage['detail'] = str(ex)
        #     returnStatus = 401
    else:
        returnMessage['detail'] = "非post请求"
        returnStatus = 401
    response.status_code = returnStatus
    response.content = json.dumps(returnMessage)
    return response

@csrf_exempt
def auth(request):
    returnMessage = {}
    returnStatus = 401
    if request.method == "GET":
        try:
            token = request.COOKIES["token"]
            user = models.User.objects.get(token = token)
            if user:
                returnMessage['name'] = user.name
                returnMessage['email'] = user.email
                returnStatus = 200
            else:
                returnMessage["detail"] = "登录失效，请重新登录"
                returnStatus = 401
        except Exception as ex:
            returnMessage["detail"] = "未登录"
            returnStatus =401
    return HttpResponse(json.dumps(returnMessage),status = returnStatus)