from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import models
import hashlib
import os

dirDataLabeled = 'data/labeled/'
fnres = 'Bai.txt'
dirDataRaw = 'data/raw/'
@csrf_exempt
def rawdata(request):
    returnMessage = {}
    if request.method == "POST":
        logfile = open('log.txt','w',encoding = 'utf-8')
        datafile = request.FILES.get("datafile")
        # task = request.POST.get('task')
        if datafile:
            des = open(dirDataRaw+datafile.name,'wb+')
            for chunk in datafile.chunks():
                des.write(chunk)
            des.close()
            des = open(dirDataRaw+datafile.name,'r',encoding = "utf-8")
            for line in des:
                try:
                    # qa = line.replace('\n','').split('\t')/
                    data = models.DataBai(sentence = line)
                    data.save()
                except Exception as ex:
                    logfile.write(line)
            des.close()
    returnMessage['detail'] = "写入成功"
    return HttpResponse(json.dumps(returnMessage),200)

def getUnlabeled():
    data = models.DataBai.objects.filter(status = 0).first()
    if not data:
        data = models.DataBai.objects.filter(status = 1).first()
    return data

def saveResult(data,result):
    f = open(dirDataLabeled+fnres,'a',encoding = 'utf-8')
    res = {}
    res['sentence'] = data.sentence
    res['results'] = result
    f.write(json.dumps(res,ensure_ascii=False)+"\n")

@csrf_exempt
def readtext(request):
    returnMessage ={}
    returnStatus = 401
    response = HttpResponse()
    if request.method == "GET":
        data = getUnlabeled()
        if not data:
            returnMessage['detail'] = "数据已标注完"
            returnStatus = 401
        else:
            returnMessage['sentence'] = data.sentence
            print(returnMessage)
            data.status = 1
            data.save()
            response.set_cookie("id",data.id)
            returnStatus= 200
    elif request.method == "POST":
        id = request.COOKIES['id']
        data = models.DataBai.objects.get(id = id)
        if data.status == 2:
            returnMessage['detail'] = "数据被标注"
            returnStatus = 401
        else:
            result = json.loads(request.body)['results']
            data.status = 2
            data.save()
            saveResult(data,result)  
            returnMessage['detail'] = "标注成功"
            returnStatus = 200
    response.content = json.dumps(returnMessage)
    response.status_code = returnStatus
    return response
        