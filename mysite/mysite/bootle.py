    #! /usr/bin/env python
    # coding=utf-8
    #自动作诗
    __author__ = 'wwj'
    from bottle import *
    import hashlib
    #解析xml
    import xml.etree.ElementTree as ET
    #解析json，给客户端发送数据，用json格式
    import json
    import requests  #第三方库
    from BeautifulSoup import BeautifulSoup  #第三方库，bae下自带    

    app = Bottle()

    @app.get("/")
    #url接口，接收微信的消息
    def check_signature():
        #检验token，如果没有这个的话，该服务器会被微信验证失败
        token = "your token" #set your token here
        signature = request.GET.get('signature', None)  
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)
        tmpList = [token, timestamp, nonce]
        tmpList.sort()
        tmpstr = "%s%s%s" % tuple(tmpList)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == signature:
            return echostr
        else:
            return None

    def parse_msg():
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

    def writepoetry(yb="16",tc="4",mt=u"无题"):
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

    @app.post("/")
    def response_msg():
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
            return echostr

        if msg['Content'] == "hi":

          #msg['Content']用户消息，汉语还是很好解析的，没有乱七八糟编码问题
          echostr = textTpl % (
                               msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                               "hi")  #填充内容
          return echostr

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
          return echostr

        else:
          echostr = textTpl % (
                               msg['FromUserName'], msg['ToUserName'], str(int(time.time())),
                               content)  
          return echostr

    #call bae serive
    from bae.core.wsgi import WSGIApplication
    import sys, os.path
    deps_path = os.path.join(os.path.split(os.path.realpath(__file__))[0],'deps')
    sys.path.insert(0, deps_path)

    #create application
    application = WSGIApplication(app)
