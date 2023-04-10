#Spider steam and Create API
from Get_Steam_Cookies import get_file_by_json, Save_file2json
import requests
import time
import os
import json
import socket, socks #Python全局 socks5
from bs4 import BeautifulSoup
import csv

URL_Steam="https://store.steampowered.com/"

#挂梯子才能爬已拥有游戏列表，而且速度大幅提升。这里挂的是 SOCKS5
socks.set_default_proxy(socks.SOCKS5, "192.168.7.130", 65533)
socket.socket = socks.socksocket #'''

session=requests.Session() #声明Session对象

#愿望单请求头
def Set_wish_cookies2session(cookies, UserLinkID):
    #把Cookie信息放入请求中
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        #'Connection': 'keep-alive',
        'Host': 'store.steampowered.com',
        'Pragma': 'no-cache',
        'Referer': f'https://store.steampowered.com/wishlist/profiles/{UserLinkID}/',
        'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        'X-Requested-With': 'XMLHttpRequest'
        }
    session.headers.update(headers)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session


#拥有游戏总数请求头
def Set_Games_cookies2session(cookies, IsCN):
    #把Cookie信息放入请求中
    headers_CN = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        #'Connection': 'keep-alive',
        'Host': 'steamcommunity.com',
        'Pragma': 'no-cache',
        'Referer': 'https://store.steampowered.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
        }
    
    headers_Other = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        #'Connection': 'keep-alive',
        'Host': 'steamcommunity.com',
        'Pragma': 'no-cache',
        'Referer': 'https://store.steampowered.com/',
        'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }
    
    if IsCN:
        session.headers.update(headers_CN)
    else:
        session.headers.update(headers_Other)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session


def get_HTML(session, url):
    try:
        session.keep_alive =False #关掉多余链接
        response_index=session.get(url)
        status_code = response_index.status_code
    except:
        status_code = -999
        #print('爬取页面失败，请检查原因')
    
    if status_code == 200:
        return response_index.text
    else:
        print('读取失败， status_code=', str(status_code))
        return ""


#获取愿望单数据，顺便排除已经失效的Cookie。
def Get_wishlist(cookiesDict):
    Wishlist=[]
    for Information in cookiesDict['CookiesList']:
        if Information["Cookies"] != "":
            session = Set_wish_cookies2session(Information["Cookies"], 
                Information["UserLinkID"])
            UserLinkID = Information["UserLinkID"]
            url=f"https://store.steampowered.com/wishlist/profiles/{UserLinkID}/wishlistdata/?p=0&v="
            HTML=get_HTML(session, url)
            if HTML != "":
                Wishlist.append(HTML)
            else:
                Information["Cookies"]=""
        time.sleep(0.5) 
    #失效的Cookie的删除将另外设置模块，因为网不好爬不了也会误删有效Cookies
    #Save_file2json(cookiesDict, '', 'Cookies.json')
    return Wishlist


#保存愿望单到本地
def SaveWishlist(session):
    cookiesDict = get_file_by_json('', 'Cookies.json')
    Wishlist=Get_wishlist(cookiesDict)
    #print(Wishlist)
    if Wishlist:
        Save_file2json({"Wish":Wishlist}, '', 'Wish.json')
        return True
    else:
        return False


#获取拥有游戏数据，顺便排除已经失效的Cookie。
def Get_Games(cookiesDict):
    Gameslist=[]
    for Information in cookiesDict['CookiesList']:
        if Information["Cookies"] != "":
            UserLinkID = Information["UserLinkID"]
            UserID = Information["UserID"]
            if UserLinkID == UserID: #外区
                url=f"https://steamcommunity.com/profiles/{UserLinkID}/games/?tab=all"
                IsCN = False
            else: #国区
                url=f"https://steamcommunity.com/id/{UserID}/games/"
                IsCN = True
            
            session = Set_Games_cookies2session(Information["Cookies"], IsCN)
            HTML=get_HTML(session, url)
            print(HTML)
            if HTML != "":
                Gameslist.append(HTML)
            #else:
            #    Information["Cookies"]=""
        time.sleep(0.5) 
    #有失效的Cookie就删掉它
    #Save_file2json(cookiesDict, '', 'Cookies.json')
    return Gameslist



#保存拥有游戏清单到本地
def SaveGameslist(session):
    cookiesDict = get_file_by_json('', 'Cookies.json')
    Gameslist=Get_Games(cookiesDict)
    #print(Gameslist)
    if Gameslist:
        Save_file2json({"Games":Gameslist}, '', 'Games.json')
        return True
    else:
        return False

def SaveData2Json():
    if SaveWishlist(session):
        print("愿望单数据保存成功")
    else:
        print("愿望单数据保存失败")
    
    if SaveGameslist(session):
        print("已拥有游戏清单数据保存成功")
    else:
        print("已拥有游戏清单数据保存失败")


def get_GamesList(HTML):
    soup_CSS=BeautifulSoup(HTML, 'lxml')
    #Bf的CSS选择器返回的是一个迭代对象，将其先装换为列表，在取第一个就好。 
    href = list(soup_CSS.select(
        'template#gameslist_config'))[0]["data-profile-gameslist"]
    #print(type(href))
    #print(href)
    return href #re.search("\d+", href).group()



def get_Discounts_and_Prices(HTML):
    soup_CSS=BeautifulSoup(HTML, 'lxml')
    discount=soup_CSS.find(
        name="div", class_="discount_pct")
    if discount == None:
        discount = "不打折"
    else:
        discount=discount.string
    
    price=soup_CSS.find(
        name="div", class_="discount_final_price").string
    original_price=soup_CSS.find(
        name="div", class_="discount_original_price")
    
    if original_price == None:
        original_price = price
    else:
        original_price=original_price.string
    return discount, original_price, price



def Get_Has_Game_List():
    Games=[]
    GameIDs=[]
    GamesMSG=get_file_by_json('', 'Games.json')
    for HTML in GamesMSG["Games"]:
        DOMPoint = json.loads(get_GamesList(HTML)) #提取游戏列表
        User64ID = DOMPoint["strSteamId"]
        #print(type(DOMPoint))
        for rgGame in DOMPoint['rgGames']:
            if not rgGame['appid'] in GameIDs:
                GameIDs.append(rgGame['appid'])
                Games.append(rgGame['name'])
                #print("{name}, GameID{appid}，属于{User}".format(
                #    name=rgGame['name'], appid=rgGame['appid'], User=User64ID)
                #    )
    return Games, GameIDs


def Get_Wish_Game_List(GameIDs):
    CSVList=[['游戏名','价格信息','标签',
        '是否免费游戏，1是0否', '游戏ID','封面地址','评审描述','评价',
        '评论总数','评论百分比','发布日期时间戳','发布日期',
        '平台图标HTML节点','类型(物品还是游戏)','游戏截图地址',
        'review_css', '优先事项','添加代码','背景图','rank','deck_compat','是否windows游戏，1是0否']]
    WishMSGt=get_file_by_json('', 'Wish.json')
    for WistDist in WishMSGt["Wish"]:
        WistDist = json.loads(WistDist) #提取游戏列表
        for GameID, GameMSG in WistDist.items():
            if not GameID in GameIDs:
                Subs=[]
                OneGameList=[]
                #print("GameID: ", GameID)
                #print("Name: ", GameMSG["name"])
                #print("capsule: ", GameMSG["capsule"])
                #print("review_score: ", GameMSG["review_score"])
                #print("review_desc: ", GameMSG["review_desc"])
                #print("reviews_total: ", GameMSG["reviews_total"])
                #print("reviews_percent: ", GameMSG["reviews_percent"])
                #print("release_date: ", GameMSG["release_date"])
                #print("release_string: ", GameMSG["release_string"])
                #print("platform_icons: ", GameMSG["platform_icons"])
                ##print("subs_ID: ", GameMSG["subs"])
                for SubMSG in GameMSG["subs"]:
                    ##print("subs_ID: ", SubMSG["id"])
                    ##print("解析前的 discount_block: ", SubMSG["discount_block"])
                    discount, original_price, price = get_Discounts_and_Prices(
                        SubMSG["discount_block"])
                    ##print("discount: ", discount)
                    ##print("original_price: ", original_price)
                    ##print("price: ", price)
                    SubsText = "物品ID: " + str(SubMSG["id"]) + ', 折扣：' + (
                        discount + '，原价：' + original_price + '，现价：') + (
                        price) 
                    Subs.append(SubsText)
                    ##print("subs_discount_pct: ", SubMSG["discount_pct"])
                    ##print("subs_price: ", SubMSG["price"])
                #print("price: " , Subs)
                #print("type: ", GameMSG["type"])
                #print("screenshots: ", GameMSG["screenshots"])
                #print("review_css: ", GameMSG["review_css"])
                #print("priority: ", GameMSG["priority"])
                #print("added: ", GameMSG["added"])
                #print("background: ", GameMSG["background"])
                #print("rank: ", GameMSG["rank"])
                #print("tags: ", GameMSG["tags"])
                #print("is_free_game: ", GameMSG["is_free_game"])
                #print("deck_compat: ", GameMSG["deck_compat"])
                #print("win: ", GameMSG["win"])
                #print("mac: ", GameMSG["mac"])
                #print("linux: ", GameMSG["linux"])
                #print('\n')
                OneGameList.append(GameMSG["name"])
                OneGameList.append(Subs)
                OneGameList.append(GameMSG["tags"])
                OneGameList.append(GameMSG["is_free_game"])
                OneGameList.append(GameID)
                OneGameList.append(GameMSG["capsule"])
                OneGameList.append(GameMSG["review_score"])
                OneGameList.append(GameMSG["review_desc"])
                OneGameList.append(GameMSG["reviews_total"])
                OneGameList.append(GameMSG["reviews_percent"])
                OneGameList.append(int(GameMSG["release_date"]))
                OneGameList.append(GameMSG["release_string"])
                OneGameList.append(GameMSG["platform_icons"])
                OneGameList.append(GameMSG["type"])
                OneGameList.append(GameMSG["screenshots"])
                OneGameList.append(GameMSG["review_css"])
                OneGameList.append(GameMSG["priority"])
                OneGameList.append(int(GameMSG["added"]))
                OneGameList.append(GameMSG["background"])
                OneGameList.append(GameMSG["rank"])
                OneGameList.append(GameMSG["deck_compat"])
                OneGameList.append(GameMSG["win"])
                CSVList.append(OneGameList)
    return CSVList

def clearData():
    Games, GameIDs=Get_Has_Game_List()
    CSVList=Get_Wish_Game_List(GameIDs)
    if len(CSVList) > 1:
        with open('愿望单.csv', 'w', encoding='utf-8-sig', newline="") as csv_file:
            writer = csv.writer(csv_file, dialect='excel')
            writer.writerows(CSVList)
            print('愿望单生成完成')


def main():
    #SaveData2Json()
    clearData()

if __name__=="__main__":
    main()#'''
