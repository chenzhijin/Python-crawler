#抓取新浪国内新闻的内容
import requests,json,pandas,re
from bs4 import BeautifulSoup

#利用地址中的新闻序号，得到新闻评论数地址，然后在js中抓取评论数
commentsurl  = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=gn&newsid=comos-{}&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20&jsvar=loader_1507605510299_18279329'
def getCommentCount(newsurl):
    m = re.search('doc-i(.*).shtml',newsurl)    #利用正则表达式在地址中抓取新闻序号
    newsid = m.group(1)
    comments = requests.get(commentsurl.format(newsid)) #利用str.format('')在字符串的{}中插入特定字符，得到新闻评论数地址，request.get()得到js代码
    #print (comments)只是得到<Response [200]>,comment.text才能得到js的代码, json.loads()用来解析js代码，返回list
    jd = json.loads(comments.text.strip('var loader_1507605510299_18279329='))  #js代码前有变量名
    return jd['result']['count']['total']   #得到评论数

#利用新闻地址获取新闻内容
def getnews(newsurl):
    newsContent = {}
    res = requests.get(newsurl)
    res.encoding=('utf-8')
    soup = BeautifulSoup(res.text,'html.parser')    #同理res.text来获取代码，BeautifulSoup来解析HTML的结构，返回list
    newsContent['tilte']=soup.select('#artibodyTitle')[0].text  #soup.select()可以用来寻找特定便签下的内容
    newsContent['time']=soup.select('#navtimeSource')[0].contents[0].strip()
    newsContent['source']=soup.select('.time-source span a')[0].text
    newsContent['editor']=soup.select('.article-editor')[0].text.lstrip('责任编辑：')
    newsContent['comment'] =getCommentCount(newsurl)
    newsContent['article']=' '.join([cont.text.strip().lstrip('原标题：') for cont in soup.select('#artibody p')[:-1]])
    return (newsContent)

#利用网页地址，抓取该网页下的所有新闻链接(在js中），利用上面两个函数获取新闻内容，放入列表中
def parseListLinks(url):
    newsdetails=[]
    res=requests.get(url)
    jd = json.loads(res.text.lstrip(' newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        #print(ent['url'])
        newsdetails.append(getnews(ent['url']))
    return (newsdetails)

#url为每个网页的通用地址，而一个网页含有多个新闻标题和链接，用for循环载入多个网页地址
url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}'
newsTotal = []
for i in range(1,3):
    url = url.format(i)
    newsTotal.extend(parseListLinks(url))

#利用pandas解析list结构
df = pandas.DataFrame(newsTotal)
df.to_excel('news.xlsx')
