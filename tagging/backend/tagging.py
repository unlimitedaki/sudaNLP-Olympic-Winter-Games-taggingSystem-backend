from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import models
import hashlib
import os
from django.db import transaction

dirDataRaw = 'data/raw/'
dirDataLabeled = 'data/labeled/'
fnres = 'tagged.txt'
@csrf_exempt
def makedata(request):
    models.Data.objects.all().delete()
    # if request.method == "GET":
    #     for i in range(1,5):
    #         data = models.Data(question = str(i),answer = str(i*2),turn = 0,task ="SUDA" )
    #         data.save()
    #     for i in range(6,10):
    #         data = models.Data(question = str(i),answer = str(i*2),turn = 0,task ="FUDAN" )
    #         data.save()
    return HttpResponse("",200)

@csrf_exempt
def loaddata(request):
    returnMessage = {}
    if request.method == "POST":
        logfile = open('log.txt','w',encoding = 'utf-8')
        datafile = request.FILES.get("datafile")
        task = request.POST.get('task')
        if datafile:
            des = open(dirDataRaw+datafile.name,'wb+')
            for chunk in datafile.chunks():
                des.write(chunk)
            des.close()
            des = open(dirDataRaw+datafile.name,'r',encoding = "utf-8")
            for line in des:
                try:
                    qa = line.replace('\n','').split('\t')
                    data = models.Data(question = qa[0],answer = qa[1],turn = 0,task =task)
                    data.save()
                except Exception as ex:
                    print(ex)
                    print(line)
                    # for l in qa:
                    #     logfile.write(l)
            des.close()
    returnMessage['detail'] = "写入成功"
    return HttpResponse(json.dumps(returnMessage),200)

# @csrf_exempt
# def savedata(request):

def checkuser(user,dataset):#检查可以标注的数据是否被当前用户标注过
    if not dataset:
        return None
    for d in dataset:
        if d.turn == 0:
            return d
        elif d.turn == 1:
            if d.user != user:
                return d
        elif d.turn == 2:
            users = d.user.split('#')
            flag = 1
            for u in users:
                if u == user:
                    flag = 0
            if flag:
                return d
    return None

@transaction.atomic
def getUnlabeled(user,task):#获取一个当前用户可以标注的数据
    allUnlabeled = models.Data.objects.select_for_update().filter(status = 0,task = task)
    res = checkuser(user,allUnlabeled)
    if not res:
        allUnlabeled = models.Data.objects.select_for_update().filter(status = 1,task = task)
        res = checkuser(user,allUnlabeled)
    if not res:
        allUnlabeled = models.Data.objects.select_for_update().filter(status = 2,task = task)
        res = checkuser(user,allUnlabeled)  
    if res:
        res.status += 1
        res.save()
    return res
   
@csrf_exempt
def next(request):#为当前用户获取一个标注任务
    returnMessage = {}
    returnStatus = 401
    response = HttpResponse()
    if request.method == "GET":
        try:
            user = request.COOKIES['email']
            task = request.GET.get('task')
            if not user:
                returnMessage['detail'] = '未登录'
                returnStatus = 401
            else:
                unlabeled = getUnlabeled(user,task)
                if not unlabeled:
                    returnMessage['detail']= "数据集已标注完"
                    returnStatus = 401
                else:
                    returnMessage['question'] = unlabeled.question
                    returnMessage['answer'] = unlabeled.answer
                    response.set_cookie('id',unlabeled.id)
                    # unlabeled.status =unlabeled.status+ 1
                    # unlabeled.save()
                    returnStatus = 200
                    print(unlabeled.id)
        except Exception as ex:
            returnMessage['detail'] = str(ex)
            returnStatus = 401
    response.status_code = returnStatus
    response.content = json.dumps(returnMessage)
    return response


def saveResult(data):
    fn = data.task + '.txt'
    f = open(dirDataLabeled+fn,'a',encoding ='utf-8')
    res = {}
    res['question'] = data.question
    res['answer'] = data.answer
    res['sentenceType'] = data.sentenceType
    res['intentionType'] = data.intentionType
    res['user'] = data.user
    print(res)
    f.write(json.dumps(res,ensure_ascii=False)+"\n")

    f.close()

@csrf_exempt
@transaction.atomic
def result(request):#接收用户的标注结果
    returnMessage = {}
    returnStatus = 401
    response = HttpResponse()
    if request.method == 'POST':
        req = json.loads(request.body.decode("utf-8"))
        qid = request.COOKIES['id']
        data = models.Data.objects.select_for_update().get(id = qid)
        # print(data.status)
        if data.turn == 3:#已被他人标注完的情况，前端已保证不会出现
              returnMessage['detail'] = "已被标注"
              returnStatus = 401
        else:
            if data.turn == 0:
                data.sentenceType = req['sentenceType']
                data.intentionType = req['intentionType']
                data.turn =data.turn+ 1
                # data.status = 0
                data.user = request.COOKIES['email']
                data.save()
            else:
                if data.sentenceType ==  req['sentenceType'] and data.intentionType == req['intentionType']:
                    data.turn = 3
                    data.status =3
                else:
                    data.turn =data.turn+ 1
                    data.status =data.turn
                data.sentenceType += '#'+req['sentenceType']
                data.intentionType += '#'+req['intentionType']
                data.user += '#'+request.COOKIES['email']
                data.save()
            returnMessage['detail'] = "标注成功"
            returnStatus = 200
            response.status_code = returnStatus
            if data.turn == 3:
                saveResult(data)
    response.content = json.dumps(returnMessage)
    return response

def recover(request):
    dataset = models.Data.objects.filter(turn = 3)
    for data in dataset:
        data.status = 3
        data.save()
    dataset = models.Data.objects.filter(turn = 2)
    for data in dataset:
        data.status = 2
        data.save()
    returnMessage = {}
    returnMessage['detail'] = "写入成功"
    return HttpResponse(json.dumps(returnMessage),200)

def users(request):
    fnuser = 'user.txt'
    fu = open(dirDataLabeled+fnuser,'w',encoding = 'utf-8')
    # usr = {}
    alluser = models.User.objects.all()
    for user in alluser:
        fu.write(user.email+'\t'+user.name+'\n')
    returnMessage = {}
    returnMessage['detail'] = "写入成功"
    return HttpResponse(json.dumps(returnMessage),200)