#!/usr/bin/python
#coding:utf-8
#By T00ls.Net
import sys
import re
reStr=re.compile(r"^\s*([^\:]+)\:(\d+)")

urls=[]
with open(sys.argv[1],'r') as f:
    for line in f:
        line = line.strip()
        m=reStr.findall(line)
        if m :
            if m[0][1] == '9443' or m[0][1] == '443' or m[0][1] == '8443':
                #print m[0][1]
                #urls.append('https://'+m[0][0])
                urls.append('https://'+line)
            else:
                urls.append('http://'+line)

with open(sys.argv[2],'w') as f:
    for line in urls:
        f.write(line+"\r\n")
