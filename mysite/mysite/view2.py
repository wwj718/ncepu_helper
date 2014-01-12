# -*- coding: utf-8 -*-  
from django.http import HttpResponse  
from django.template import RequestContext, Template  
from django.views.decorators.csrf import csrf_exempt  
from django.utils.encoding import smart_str, smart_unicode  
  
import xml.etree.ElementTree as ET  
import urllib,urllib2,time,hashlib  
   
from toolsviews import writepoetry,youdaofy,textTpl,pictextTpl

import logging
import time
logging.basicConfig(filename='E:\wwj\weixin\weixin\develop.log',level=logging.DEBUG)
logging.debug('This message should go to the log file --*%s*',time.ctime())
logging.info('So should this %s',time.ctime())
logging.warning('And this %s %d, too','123',1)

TOKEN = "wwjtest"  
  
YOUDAO_KEY = "308182932"
YOUDAO_KEY_FROM = "wwjweixin"  
YOUDAO_DOC_TYPE = "xml"  
 
@csrf_exempt  
def handleRequest(request):  
    #入口
    logging.debug('begin --*%s*',time.ctime())

    if request.method == 'GET':  
        #response = HttpResponse(request.GET['echostr'],content_type="text/plain")  
        response = HttpResponse(checkSignature(request),content_type="text/plain")  
        return response  
    elif request.method == 'POST':  
        #c = RequestContext(request,{'result':responseMsg(request)})  
        #t = Template('{{result}}')  
        #response = HttpResponse(t.render(c),content_type="application/xml")  
        response = HttpResponse(responseMsg(request),content_type="application/xml")  
        return response  
    else:  
        return None  
  
def checkSignature(request):  
    #验证服务器有效性,功能函数
    global TOKEN  
    signature = request.GET.get("signature", None)  
    timestamp = request.GET.get("timestamp", None)  
    nonce = request.GET.get("nonce", None)  
    echoStr = request.GET.get("echostr",None)  
  
    token = TOKEN  
    tmpList = [token,timestamp,nonce]  
    tmpList.sort()  
    tmpstr = "%s%s%s" % tuple(tmpList)  
    tmpstr = hashlib.sha1(tmpstr).hexdigest()  
    if tmpstr == signature:  
        return echoStr  
    else:  
        return None  

def userMsg(request):
    #最终返回信息
    rawStr = smart_str(request.raw_post_data)  #工具函数
    #rawStr = smart_str(request.POST['XML'])  
    msg = paraseMsgXml(ET.fromstring(rawStr))
    logging.debug('msg:%s --*%s*',msg,time.ctime())
    #queryStr = msg.get('Content','You have input nothing~')  #来自用户
    return msg



def responseMsg(request):  
    #最终返回信息
    msg = userMsg(request)
    queryStr = msg.get('Content','You have input nothing~')  #来自用户
    #用户的输入 queryStr

    #处理关注事件
    #调试成功，技巧：控制变量，从最少元素开始，逐步增加
    if msg["MsgType"] == "event":
        content ='感谢关注ncepunmc微信公众平台'
        return getReplyXml(msg,content)

    if queryStr=='1':
        #钩子
        return getReplyXml(msg,'你输入的是1')
    elif 'fy' in queryStr:
        try:
            queryStr=queryStr.split("#")[-1]
        except:
            queryStr=queryStr.split("#")[-1]        
        raw_youdaoURL = "http://fanyi.youdao.com/openapi.do?keyfrom=%s&key=%s&type=data&doctype=%s&version=1.1&q=" % (YOUDAO_KEY_FROM,YOUDAO_KEY,YOUDAO_DOC_TYPE)     
        youdaoURL = "%s%s" % (raw_youdaoURL,urllib2.quote(queryStr))  
        req = urllib2.Request(url=youdaoURL)  
        result = urllib2.urlopen(req).read()  
        replyContent = paraseYouDaoXml(ET.fromstring(result))  #返回数据  
        return getReplyXml(msg,replyContent)
    elif 'sc' in queryStr:
        try:
            content=queryStr.split("#")[-1]
        except:
            content=queryStr.split("#")[-1]
        #content="怀"
        mypoetry=writepoetry(mt=content)
        return getReplyXml(msg,mypoetry)
    else:
        content='''当前有两个可用功能（翻译，自动作诗）：\n 翻译：输入示例: fy#你好 \n 诗词：输入示例: sc#登山'''
        return getReplyXml(msg,content)  
  
def paraseMsgXml(rootElem): 
    # rootElem  微信发过来的数据
    #解析xml(微信发过来的数据)
    msg = {}  
    if rootElem.tag == 'xml':  
        for child in rootElem:  
            msg[child.tag] = smart_str(child.text)  
    return msg  #结构化信息,视为列表
  
def paraseYouDaoXml(rootElem):  
    #工具函数 解析有道数据
    replyContent = ''  
    if rootElem.tag == 'youdao-fanyi':  
        for child in rootElem:  
            # 错误码  
            if child.tag == 'errorCode':  
                if child.text == '20':  
                    return 'too long to translate\n'  
                elif child.text == '30':  
                    return 'can not be able to translate with effect\n'  
                elif child.text == '40':  
                    return 'can not be able to support this language\n'  
                elif child.text == '50':  
                    return 'invalid key\n'  
  
            # 查询字符串  
            elif child.tag == 'query':  
                replyContent = "%s%s\n" % (replyContent, child.text)  
  
            # 有道翻译  
            elif child.tag == 'translation':   
                replyContent = '%s%s\n%s\n' % (replyContent, '-' * 3 + u'翻译' + '-' * 3, child[0].text)  
  
            # 有道词典-基本词典  
            elif child.tag == 'basic':   
                replyContent = "%s%s\n" % (replyContent, '-' * 3 + u'基本词典' + '-' * 3)  
                for c in child:  
                    if c.tag == 'phonetic':  
                        replyContent = '%s%s\n' % (replyContent, c.text)  
                    elif c.tag == 'explains':  
                        for ex in c.findall('ex'):  
                            replyContent = '%s%s\n' % (replyContent, ex.text)  
  
            # 有道词典-网络释义  
            elif child.tag == 'web':   
                replyContent = "%s%s\n" % (replyContent, '-' * 3 + u'网络释义' + '-' * 3)  
                for explain in child.findall('explain'):  
                    for key in explain.findall('key'):  
                        replyContent = '%s%s\n' % (replyContent, key.text)  
                    for value in explain.findall('value'):  
                        for ex in value.findall('ex'):  
                            replyContent = '%s%s\n' % (replyContent, ex.text)  
                    replyContent = '%s%s\n' % (replyContent,'--')  
    return replyContent  
  
def getReplyXml(msg,replyContent):  
    extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";  
    extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)  #replyContent内容
    return extTpl  

