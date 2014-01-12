#! /usr/bin/env python
# coding=utf-8
#音乐  ， 电影 ，书籍
__author__ = 'wwj'

import hashlib
#解析xml
import xml.etree.ElementTree as ET
#抓取分析网页数据
import urllib2
#解析json，给客户端发送数据，用json格式
import json

import requests
#import sae.BeautifulSoup
from BeautifulSoup import BeautifulSoup 


from django.http import HttpResponse
import datetime

def home(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

# def weixin(request):
#     now = datetime.datetime.now()
#     html = "<html><body>test weixin.</body></html>"
#     return HttpResponse(html)

def weixin(request):
#只有get and post
  if request.method == 'GET':
    return check_signature(request)

  if request.method == 'POST':
    return response_msg(request)



#url接口，接收微信的消息
def check_signature(request):
    #检验token，如果没有这个的话，该服务器会被微信验证失败
    token = "wwjtest" #set your token here
    signature = request.GET.get('signature', None)  
    timestamp = request.GET.get('timestamp', None)
    nonce = request.GET.get('nonce', None)
    echostr = request.GET.get('echostr', None)
    tmpList = [token, timestamp, nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    hashstr = hashlib.sha1(tmpstr).hexdigest()
    if hashstr == signature:
        return HttpResponse(echostr)
    else:
        return HttpResponse(None)
 
def parse_msg(request):
    #解析来自微信的请求，request用于传递请求信息，这是bootle的知识，与微信无关，核心只是普通的url get部分内容
    recvmsg = request.body.read()  
    root = ET.fromstring(recvmsg)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg
 
def set_content():
    content = '''添加自动作诗模块，输入"诗词#登山"自动写作主题为登山的诗词,目前仅支持平水韵五绝，之后会添加其他体裁'''
    return content
#电影查询
def query_movie_info():
    movieurlbase = "http://api.douban.com/v2/movie/search"
    DOUBAN_APIKEY =  "08cbc4f981e88c301a634eec85b9a490"  # 这里需要填写你自己在豆瓣上申请的应用的APIKEY
    movieinfo = parse_msg()
    #movieinfo["Content"]，是来自用户的信息，用一个函数处理一下吧，要求带有某些东西 比如#
    searchkeys = urllib2.quote(movieinfo["Content"].encode("utf-8"))  # 如果Content中存在汉字，就需要先转码，才能进行请求
    url = '%s?q=%s&apikey=%s' % (movieurlbase, searchkeys, DOUBAN_APIKEY)
    # return "<p>{'url': %s}</p>" % url
    # url = '%s%s?apikey=%s' % (movieurlbase, id["Content"], DOUBAN_APIKEY)
    # resp = requests.get(url=url, headers=header)
    resp = urllib2.urlopen(url)
    movie = json.loads(resp.read())
    # return "<p>{'movie': %s}</p>" % movie
    # info = movie["subjects"][0]["title"] + movie["subjects"][0]["alt"]
    # info = movie['title'] + ': ' + ''.join(movie['summary'])
    return movie
    # return info
 
def query_movie_details():
    movieurlbase = "http://api.douban.com/v2/movie/subject/"
    DOUBAN_APIKEY =  "08cbc4f981e88c301a634eec85b9a490"  # 这里需要填写你自己在豆瓣上申请的应用的APIKEY
    id = query_movie_info()
    url = '%s%s?apikey=%s' % (movieurlbase, id["subjects"][0]["id"], DOUBAN_APIKEY)
    resp = urllib2.urlopen(url)
    description = json.loads(resp.read())
    description = ''.join(description['summary'])
    return description 
 

def writepoetry(request,yb="1",tc="1",mt=u"无题"):
  #yb是韵部，tc是体裁，mt是命题
    #mt必须是u
  cleanmt=mt.encode("GBK")
  input={'yb':yb, "tc":tc,'mt':cleanmt}
  r = requests.post("http://www.poeming.com/web/main.asp", data=input)
  cleandate=r.content.decode("GBK") #现在是utf-8，在程序中保持为unicode,直到输出才化为utf-8
  outdate=(cleandate.encode("utf-8"))
  #print outdate
  soup = BeautifulSoup(outdate) 
  p = soup.findAll('p')
  #p是list
  #p[1]是主要内容
  p_text=p[1].text[2:] 
  return p_text
  ##成功后的内容
  #p_list=p_text.split(u"。")#使用句号分割取出
  #print ''.join(p_list[1:])
  #Out[8]: {'confidence': 0.99, 'encoding': 'GB2312'}
  #mypoetry=writepoetry(yb="2",tc="1",mt=u"无题")


  
def response_msg(request):
  #返回消息到客户端 
    msg = parse_msg() 
    #解析接收到的用户消息
    #处理文本消息，注意必须按照微信接口要求的格式，图片消息的话应该给出图片url,多参考别人的源码
    textTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[text]]></MsgType>
             <Content><![CDATA[%s]]></Content>
             <FuncFlag>0</FuncFlag>
             </xml>"""  
    echostr = textTpl % (
            msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 
            '''添加自动作诗模块，输入"诗词#登山"自动写作主题为登山的诗词,目前仅支持平水韵五绝，之后会添加其他体裁''')
    return HttpResponse(echostr,content_type="application/xml")
    #<MsgType><![CDATA[text]]></MsgType>  这里不用%s才能显示关注？？
    #图片模板
    pictextTpl = """<xml>
      <ToUserName><![CDATA[%s]]></ToUserName>
      <FromUserName><![CDATA[%s]]></FromUserName>
      <CreateTime>%s</CreateTime>
      <MsgType><![CDATA[news]]></MsgType>
      <ArticleCount>1</ArticleCount>
      <Articles>
      <item>
      <Title><![CDATA[%s]]></Title>
      <Description><![CDATA[%s]]></Description>
      <PicUrl><![CDATA[%s]]></PicUrl>
      <Url><![CDATA[%s]]></Url>
      </item>
      </Articles>
      <FuncFlag>1</FuncFlag>
      </xml> """
    
    content = set_content()
    #处理关注事件
    #调试成功，技巧：控制变量，从最少元素开始，逐步增加
    if msg["MsgType"] == "event":
        echostr = textTpl % (
            msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 
            '''添加自动作诗模块，输入"诗词#登山"自动写作主题为登山的诗词,目前仅支持平水韵五绝，之后会添加其他体裁''')
        return HttpResponse(echostr)
    
    if msg['Content'] == "hi":

      #msg['Content']用户消息，汉语还是很好解析的，没有乱七八糟编码问题
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           "hi")  #填充内容
      return HttpResponse(echostr)
    
    elif "诗词" in msg['Content']: #“#”只能用中文
      try:
        content=msg['Content'].split("#")[-1]
      except:
        content=msg['Content'].split("#")[-1]
      #content="怀"
      mypoetry=writepoetry(yb="2",tc="1",mt=content)
      #msg['Content']用户消息，汉语还是很好解析的，没有乱七八糟编码问题
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           mypoetry)  #填充内容
      return HttpResponse(echostr)
    
    elif "电影" in msg['Content']: #“#”只能用中文
      try:
        content=msg['Content'].split("#")[-1]
      except:
        content=msg['Content'].split("#")[-1]
        Content = query_movie_info()
        description = query_movie_details()
        echostr = pictextTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                                Content["subjects"][0]["title"], description,
                                Content["subjects"][0]["images"]["large"], Content["subjects"][0]["alt"])
      return HttpResponse(echostr)
    
    elif msg['Content'] == "test2":
      #测试requests 包是否可用
      r = requests.post("http://www.baidu.com")#也就是说有requests,也就是说这个是有效的，才返回
      a=r.text[0:5]
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           a)  #填充内容,返回了！！
      return HttpResponse(echostr)
    elif msg['Content'] == "图片":
      echostr = pictextTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           "标题","简介","http://59.67.225.73/jiaowuchu/images/green/service.gif",
              "http://wwj718.github.io")  #填充内容,最后两个是图片链接和内容地址链接
      return HttpResponse(echostr)
    else:
      echostr = textTpl % (
                           msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                           content)  
      return HttpResponse(echostr)
    
      


