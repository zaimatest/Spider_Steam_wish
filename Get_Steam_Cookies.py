import requests
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re

#"https://help.steampowered.com/zh-cn/login/" 这个连接是从客服进去
#"https://store.steampowered.com/login/" 正常的login
BASE_URL="https://store.steampowered.com/login/?redir=&redir_ssl=1&snr=1_4_springsale__global-header"
INDEX_URL="https://store.steampowered.com/"

ua_random="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
TIME_OUT=1000 #超时


#初始化
def Set_Browser():
    option=ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument(f'user-agent="{ua_random}"')
    option.add_argument("--disable-blink-features=AutomationControlled")

    browser=webdriver.Chrome(options=option)
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',{
        'source':'Object.defineProperty(navigator, "webdriver", {get: () => False})'
        }) 
        
    return browser


def iselement(browser, locator, wait):
    try:。
        wait.until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 
            locator)))
        return True
    except TimeoutException:
        print("超市了")
        return False

def login_Steam(browser, USERNAME, PASSWORD, wait):
    #检测登录页面直到出现登陆按钮
    while True:
        if iselement(browser, 'button.newlogindialog_SubmitButton_2QgFE', wait):
            break

    #模拟输入用户名、密码，并点击登陆按钮登陆。
    browser.find_element(By.CSS_SELECTOR, 
        'input.newlogindialog_TextInput_2eKVn[type="text"]').send_keys(USERNAME)
    browser.find_element(By.CSS_SELECTOR, 
        'input.newlogindialog_TextInput_2eKVn[type="password"]').send_keys(PASSWORD)
    browser.find_element(By.CSS_SELECTOR, 
        'button.newlogindialog_SubmitButton_2QgFE').click()

#获取用户链接ID
def get_UserID(HTML):
    #print(HTML)
    soup_CSS=BeautifulSoup(HTML, 'lxml') 
    href = list(soup_CSS.select('div.playerAvatar a'))[0]["href"]
    print(type(href))
    return re.search("\d+", href).group()


#从 Cookies 获取用户Steam 64位ID
def get_User64ID(Text):
    return re.search("7656\d+", Text).group()

def get_new_cookies(browser, USERNAME, PASSWORD):
    #初始化浏览器
    if browser == None:
        browser = Set_Browser()
    wait = WebDriverWait(browser, TIME_OUT) #超时设置：配置页面加载的最长等待时间
    
    #通过Selenium访问登陆页面
    if browser.current_url != BASE_URL:
        browser.get(BASE_URL)
    
    login_Steam(browser, USERNAME, PASSWORD, wait);
    
    #持续到愿望单标签出现
    while True:
        if iselement(browser, 'a#wishlist_link', wait):
            break

        print("检测重试按钮")
        #如果出现重试按钮，点击它
        if iselement(browser, 'button.newlogindialog_TryAgainButton_GMIRO', wait):
            browser.find_element(By.CSS_SELECTOR, 
                'button.newlogindialog_TryAgainButton_GMIRO').click()
        
        #检测是否需要再登陆
        if iselement(browser, 
            'input.newlogindialog_TextInput_2eKVn[type="text"]', wait):
            login_Steam(browser, USERNAME, PASSWORD, wait);
        time.sleep(0.5)


    #从浏览器对象中获取Cookie信息
    cookies=browser.get_cookies()
    #获取用户ID，注意，国区的64位ID和用户ID是不一样的，外区用户ID即是64位ID
    UserID=get_UserID(browser.page_source)
    #从Cookie获取64位ID
    for cookie in cookies:
        if cookie['name'] == 'steamLoginSecure':
            UserLinkID=get_User64ID(cookie['value'])
    
    print('Cookies、UserLinkID、UserID获取成功')

    # 不能注销，注销后Cookie就是离线状态了，这里直接关闭
    #需要定位的注销节点在页面中被隐藏了，这个时候需要让元素在页面上可见，才可操作
    #browser.find_element(By.CSS_SELECTOR, 'span#account_pulldown').click()
    #browser.find_element(By.CSS_SELECTOR, 'a[href="javascript:Logout();"]').click()
    #print("注销当前账号")
    #while True:
    #    if iselement(browser, 'a.global_action_link', wait):
    #        browser.find_element(By.CSS_SELECTOR, 'a.global_action_link').click()
    #        print("进入登陆页面，等待下一次登陆或关闭浏览")
    #        break
    browser.close()
    browser = None
    return cookies, UserLinkID, UserID, browser

#初始化session会话
def Set_session():
    headers = {'User-Agent': 
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
    session=requests.Session() #声明Session对象
    session.headers.update(headers)
    session.keep_alive =False #关掉多余链接
    return session

#获取Steam首页，用于检测cookie和截取用户连接ID
def get_SteamHTML(cookies, session):
    #把Cookie信息放入请求中
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    response=session.get(INDEX_URL)
    return response

#检测Cookie是否有效
def Test_One_cookies(response):
    if response.status_code == 200:
        #print('response url', response.url) #这里返回的是主页面的url，模拟登录成功
        print('response Status', response.status_code)
        return True
    else:
        print('response Status', response.status_code)
        return False


def get_file_by_json(path, filename):
    Dict = None
    if not os.path.exists(path + filename):
        print('>>json文件不存在')
    else:
        with open(path + filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) != 0:
                #print(content);
                Dict = json.loads(content)
                print('>>已读取json文件', filename)
            else:
                print(f'>>json文件{filename}内容为空')
    return Dict


def Save_file2json(Dict, path, filename):
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(Dict, ensure_ascii=False, indent=4))
        print('>>已更新json文件', filename)


def check_and_updata_cookiesDict(cookiesDict):
    #response = None
    browser = None
    session = Set_session()
    for Information in cookiesDict['CookiesList']:
        if Information["Cookies"] == "":
            cookies, UserLinkID, UserID, browser=get_new_cookies(browser,
                Information["USERNAME"], Information["PASSWORD"])
            Information["UserLinkID"] = UserLinkID
            Information["Cookies"] = cookies
            Information["UserID"] = UserID
        #不再加入检测，检测移动到Get_Wish
        #else:
        #    response=get_SteamHTML(Information["Cookies"], session)
        #    if not Test_One_cookies(response):
        #        cookies, UserLinkID, UserID, browser=get_new_cookies(browser,
        #            Information["USERNAME"], Information["PASSWORD"])
        #        Information["UserLinkID"] = UserLinkID
        #        Information["Cookies"] = cookies
        #        Information["UserID"] = UserID
        #
        #if response == None:
        #    response=get_SteamHTML(Information["Cookies"], session)
        
        time.sleep(0.5)
    
    #为了让Cookies保持在登陆状态，因此在每一次获取到Cookie之后，将browser close
    #if browser != None:
    #    browser.close()
    return cookiesDict


def check_and_updata_cookiesJson():
    try:
        cookiesDict = get_file_by_json('', 'Cookies.json')
        cookiesDict = check_and_updata_cookiesDict(cookiesDict)
        print(cookiesDict)
        Save_file2json(cookiesDict, '', 'Cookies.json')
    finally:
        print("Cookies.json 更新完成")


def main():
    check_and_updata_cookiesJson()


if __name__=="__main__":
    main()#'''




