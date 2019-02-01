#!/bin/bash
#By T00ls.Net
masscan $1/24  -p80,443,6379,7001,9200,9060,9043,9990,9080,8443,9443,2809,5060,5061,8880,9401,1098,1099,4444,4445,8000-8100  --rate 100000 -oJ $1.json
cat $1.json |awk -F' ' '{print $3,$7}'|awk -F "\"" '{print $2":"$3}'|sed "s/,//g"|sed "s/\s//g" |grep -v ^: >$1.list
python masscan_checkHttp.py $1.list $1.result
python get_title.py -t $1.result
