import requests
from lxml import etree


#------------------------------------ 全局变量 ------------------------------------#
CCFAfilepath = 'CCFA_journal&conference_info.json'           # 格式化文献目录文件路径
outputpath = 'results.txt'                                   # 查询结果的输出文件路径
Results = []                                                 # 满足关键词搜索的论文 


#------------------------------------ 查询单词 ------------------------------------#
def getallwords(title):
    wordlist = []
    tmp = ''
    for i in range(len(title)):
        c = title[i]
        if len(tmp) == 0:
            if (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122):
                tmp += c
            else:
                continue
        else:
            if (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122):
                tmp += c
            else:
                wordlist.append(tmp.lower())
                tmp = ''
        if i == len(title)-1:
            wordlist.append(tmp)
    return wordlist


#------------------------------------ 主函数 ------------------------------------#
def main():
    
    print("==================================================")
    print("|         源于DBLP的CCFA论文关键词搜索工具         |")
    print("==================================================")
    
    # 读入会议/期刊网站信息文件
    infoDict = {}
    with open(CCFAfilepath, 'r', encoding='utf-8') as f:
        infoDict = eval(f.read())
    
    # 取出其中的所有领域，罗列给用户查看
    domainList = []
    domainList = list(infoDict.keys())
    if len(domainList) == 0:
        print("[error]当前读入的文件中没有任何领域名")
        return
    else:
        print("[info]当前可选的领域名及其索引序号数如下：")
        for i in range(len(domainList)):
            print(str(i+1)+":"+domainList[i])
          
    # 接受输入的领域索引序号，取出CCFA期刊和会议网站存为列表
    domainIndex = 0
    input_legality = False
    while not input_legality:
        print("[input]请输入您所需领域的索引序号数：", end='')
        domainIndex = eval(input())
        if not (domainIndex == domainIndex//1 and domainIndex >= 1 and domainIndex <= len(domainList)):
            print("[error]您输入的领域索引序号数有误，请重新输入")
            continue
        else:
            print("[input]您选择的领域为："+domainList[domainIndex-1]+"，是否确认(Y/N)：", end='')
            confirm = input()
            if not (confirm == 'y' or confirm == 'Y'):
                print("[error]您未确认领域的选择，请重新输入")
                continue
            else:
                input_legality = True
    infoList = infoDict[domainList[domainIndex-1]]
    print("[info]您所有领域下共有"+str(len(infoList))+"种各期刊/会议")
    
    # 接受输入的用户所需关键词，空格隔开
    print("[input]请输入您想查询的英文关键词：", end='')
    keywordInput = input()
    keywordList = keywordInput.split()
    
    # 循环查询每个期刊/会议的所有卷的数量和链接
    for i in range(len(infoList)):
        info = infoList[i]
        print("[info]当前正在查询第 "+str(i+1)+"/"+str(len(infoList))+" 个期刊/会议")
        website = info['website']
        res = requests.get(url=website)
        if res.status_code != 200:
            print("[error]本期刊/会议链接失效："+website)
        else:
            xpathtree = etree.HTML(res.text)
            allhrefList = xpathtree.xpath('//*/@href')
            hrefList = []
            for j in range(len(allhrefList)):
                href = allhrefList[j]
                if website.lstrip('https://').lstrip('http://') in href.lstrip('https://').lstrip('http://'):
                    hrefList.append(href)
            print("[info]当前第 "+str(i+1)+"/"+str(len(infoList))+" 期刊/会议共有 "+str(len(hrefList))+" 卷")
            
            # 循环查询当前期刊/会议每一卷内的所有论文的数量和链接
            for l in range(len(hrefList)):
                href = hrefList[l]
                res2 = requests.get(url=href)
                if res2.status_code == 200:
                    xpathtree2 = etree.HTML(res2.text)
                    allessayList = xpathtree2.xpath('//*/@href')
                    EssayList = []
                    for essayhref in allessayList:
                        if website.replace('/db/','/rec/').lstrip('https://').lstrip('http://') in essayhref.lstrip('https://').lstrip('http://'):
                            EssayList.append(essayhref)
                    print("[info]当前第 "+str(i+1)+"/"+str(len(infoList))+" 期刊/会议的第 "+str(l+1)+"/"+str(len(hrefList))+" 卷共有 "+str(len(EssayList)//8)+" 篇论文")
                    
                    # 循环查询每篇论文的元数据（名称，年份）
                    for k in range(len(EssayList)):
                        if k%8 == 0:
                            essayhref = EssayList[k]
                            res3 = requests.get(url=essayhref)
                            if res3.status_code == 200:
                                xpathtree3 = etree.HTML(res3.text)
                                titlestr = xpathtree3.xpath('//title/text()')[0]
                                yearstr = xpathtree3.xpath("//div[@class='note-line']/text()")[0]
                                wordlist = getallwords(titlestr)
                                haveAllWord = True
                                for keyword in keywordList:
                                    if keyword.lower() not in wordlist:
                                        haveAllWord = False
                                        break
                                if haveAllWord:
                                    year = yearstr.split('(')[-1][:-1]
                                    title = titlestr[5:]
                                    print("[output]找到适配论文："+title+' '+year)
                                    Results.append([title, year])
                       
        
main()
Results.sort(key=lambda x:x[1], reverse=True)    
with open(outputpath, 'w', encoding='utf-8') as f:
    for result in Results:
        f.write(str(result[0])+' '+str(result[1])+'\n')
print("[info]已将"+str(len(Results))+"篇论文按照年份降序排列存入文件中，文件路径为："+outputpath)
print("==================================================")
print("|                本次查询功能已完成                |")
print("==================================================")
