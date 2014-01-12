#! /usr/bin/env python
# coding=utf-8
#音乐  ， 电影 ，书籍
__author__ = 'wwj'

import requests

#import sae.BeautifulSoup
from BeautifulSoup import BeautifulSoup 
import chardet 
import logging
import time

def writepoetry(yb="16",tc="4",mt=u"无题"):
        #yb是韵部，tc是体裁，mt是命题
        #mt必须是u
        #cleanmt=mt.encode("GBK")
        #debug:logging.debug('wwjencode:%s --*%s*',chardet.detect(mt),time.ctime())
        cleanmt=mt.decode("utf-8")  #nice ，解码
        cleanmt=cleanmt.encode("GBK")
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

def youdaofy():
    pass

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