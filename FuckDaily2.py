import sys
import requests
import re


class FuckDaily():

    def __init__(self):
        self.username = '2203000000'  # 账号
        self.password = '000000'  # 密码

        self.severInform = '无'  # sever酱通知密钥
        # -------------------------------------------------------------------------------------------------------------
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
        }
        self.loginUrl = 'http://authserver.jit.edu.cn/authserver/login?service=http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/index.do?amp_sec_version_=1'
        self.params = {
            'pageNumber': '1'
        }
        self.state = ''

    def login(self):
        session = requests.Session()
        response = requests.get(self.loginUrl, headers=self.headers)
        # get请求，获取响应网页数据
        htmls = response.content.decode()
        # 将字典转换为字符类型，用于正则表达式提取
        it = re.findall('name="lt" value="(.*?)"/>', htmls)[0]
        execution = re.findall('name="execution" value="(.*?)"/>', htmls)[0]
        # 从get请求获取的响应网页数据，正则表达式提取lt和execution数据

        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        # 将cookie转换为字典
        route = cookies['route']
        JSESSIONID = cookies['JSESSIONID']
        # 从字典中获取route键值和JSESSIONID键值

        data = {

            "username": self.username,
            "password": self.password,
            "lt": it,
            "dllt": "userNamePasswordLogin",
            "execution": execution,
            "_eventId": "submit",
            "rmShown": "1"

        }  # 构建post表单数据/用户数据

        session.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cookie': 'route={0}; JSESSIONID={1}'.format(route, JSESSIONID),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
        }  # 构建会话请求头部

        response = session.post(self.loginUrl, data=data, allow_redirects=False)
        # 发送请求头部和用户数据并禁止session重定向用来获取MOD_AUTH_CAS值

        session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
        }  # 重构会话请求头部

        casUrl = response.headers.get('Location')
        # 获取重定向url
        ehallapp = session.get(casUrl)
        # 更新cookie值

        cookies = session.cookies
        # 最终cookies
        cookies = requests.utils.dict_from_cookiejar(cookies)

        cookies = {
            '_WEU': cookies.get('_WEU'),
            'EMAP_LANG': 'zh',
            'route': cookies.get('route'),
            'MOD_AUTH_CAS': cookies.get('MOD_AUTH_CAS'),
            'JSESSIONID': cookies.get('JSESSIONID'),
        }
        return cookies

    def time(self, cookies):
        timeUrl = 'http://ehallapp.jit.edu.cn/qljfwapp/sys/lwpub/api/getServerTime.do'
        severTime = requests.get(timeUrl, headers=self.headers, cookies=cookies)
        # 获取当前服务器时间
        timejson = severTime.json()
        time = timejson.get('date')
        DateTime = re.sub(r'/', "-", time)

        return DateTime

    def getInfo(self, cookies):
        # 获取前一天填写的表单所有信息
        infoUrl = 'http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/modules/healthClock/getMyDailyReportDatas.do'

        info = requests.post(infoUrl, headers=self.headers, cookies=cookies)
        infoJson = info.json()
        row = infoJson['datas']['getMyDailyReportDatas']['rows']
        stuInfo = row[0]
        return stuInfo

    def widInfo(self, cookies):
        widUrl = 'http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/modules/healthClock/getMyTodayReportWid.do'
        widhtml = requests.post(widUrl, cookies=cookies, headers=self.headers, data=self.params)
        widText = widhtml.text
        widDict = {}
        widObj = re.search(r'"WID":"', widText, re.M | re.I)
        if widObj:
            wid = re.findall('"WID":"(.*?)","TODAY_', widText)[0]
            CZRQ = re.findall('CZRQ":"(.*?)","BY10', widText)[0]
            widDict = {
                'wid': wid,
                'CZRQ': CZRQ,
            }

        return widDict

    def signIn(self, cookies, severTime, severDay, widDict, stuDict):
        reSaveUrl = 'http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/modules/healthClock/T_HEALTH_DAILY_INFO_SAVE.do'
        data = {
            "WID": widDict.get('wid'),
            "BY2": "",
            "BY7_DISPLAY": "否",
            "BY7": "0",
            "BY8_DISPLAY": "",
            "BY8": "",
            "CREATED_AT": severTime,
            "CZR": "",
            "CZZXM": "",
            "CZRQ": widDict.get('CZRQ'),
            "USER_ID": self.username,
            "USER_NAME": stuDict.get('USER_NAME'),
            "DEPT_CODE_DISPLAY": stuDict.get('DEPT_CODE_DISPLAY'),
            "DEPT_CODE": stuDict.get('DEPT_CODE'),
            "DEPT_NAME": stuDict.get('DEPT_NAME'),
            "PHONE_NUMBER": stuDict.get('PHONE_NUMBER'),
            "FILL_TIME": severTime,
            "CLOCK_SITUATION": stuDict.get('CLOCK_SITUATION'),
            "BY3_DISPLAY": stuDict.get('BY3_DISPLAY'),
            "BY3": stuDict.get('BY3'),
            "BY4_DISPLAY": stuDict.get('BY4_DISPLAY'),
            "BY4": stuDict.get('BY4'),
            "BY11_DISPLAY": stuDict.get('BY11_DISPLAY'),
            "BY11": stuDict.get('BY11'),

            "TODAY_SITUATION_DISPLAY": stuDict.get('TODAY_SITUATION_DISPLAY'),
            "TODAY_SITUATION": stuDict.get('TODAY_SITUATION'),
            "TODAY_CONDITION_DISPLAY": stuDict.get('TODAY_CONDITION_DISPLAY'),
            "TODAY_CONDITION": stuDict.get('TODAY_CONDITION'),
            "CONTACT_HISTORY_DISPLAY": stuDict.get('CONTACT_HISTORY_DISPLAY'),
            "CONTACT_HISTORY": stuDict.get('CONTACT_HISTORY'),
            "TODAY_NAT_CONDITION_DISPLAY": stuDict.get('TODAY_NAT_CONDITION_DISPLAY'),
            "TODAY_NAT_CONDITION": stuDict.get('TODAY_NAT_CONDITION'),
            "TODAY_VACCINE_CONDITION_DISPLAY": stuDict.get('TODAY_VACCINE_CONDITION_DISPLAY'),
            "TODAY_VACCINE_CONDITION": stuDict.get('TODAY_VACCINE_CONDITION'),
            "TODAY_HEALTH_CODE_DISPLAY": stuDict.get('TODAY_HEALTH_CODE_DISPLAY'),
            "TODAY_HEALTH_CODE": stuDict.get('TODAY_HEALTH_CODE'),
            "BY1_DISPLAY": stuDict.get('BY1_DISPLAY'),
            "BY1": stuDict.get('BY1'),
            "BY19_DISPLAY": stuDict.get('BY19_DISPLAY'),
            "BY19": stuDict.get('BY19'),
            "BY5": "",
            "BY6": "",
            "BY20": "",
            "TODAY_BODY_CONDITION_DISPLAY": "",
            "TODAY_BODY_CONDITION": "",
            "TODAY_TEMPERATURE": "",
            "TODAY_ISOLATE_CONDITION_DISPLAY": "",
            "TODAY_ISOLATE_CONDITION": "",
            "TODAY_TARRY_CONDITION_DISPLAY": "",
            "TODAY_TARRY_CONDITION": "",
            "BY17_DISPLAY": "",
            "BY17": "",
            "NEED_CHECKIN_DATE": severDay,
            "CHECKED_DISPLAY": "",
            "CHECKED": "",
            "BY18_DISPLAY": "",
            "BY18": "",
            "BY9_DISPLAY": "",
            "BY9": "",
            "BY10_DISPLAY": "",
            "BY10": "",
            "BY16_DISPLAY": "",
            "BY16": "",
            "BY12_DISPLAY": "",
            "BY12": "",
            "BY13_DISPLAY": "",
            "BY13": "",
            "BY14_DISPLAY": "",
            "BY14": "",
            "BY15_DISPLAY": "",
            "BY15": ""
        }
        signIn = requests.post(reSaveUrl, data=data, headers=self.headers, cookies=cookies)
        signJson = signIn.json()
        print(signJson)

    def severChan(self, severDay):
        # sever酱微信通知
        url = 'https://sctapi.ftqq.com/{}.send'.format(self.severInform)
        info = severDay + ' 健康打卡~'
        form = {
            'title': info
        }
        response = requests.post(url, data=form)

    def run(self):
        cookies = FuckDaily.login(self)
        severTime = FuckDaily.time(self, cookies)
        severDay = re.findall('(.*?) ', severTime)[0]
        widDict = FuckDaily.widInfo(self, cookies)
        stuInfo = FuckDaily.getInfo(self, cookies)
        FuckDaily.signIn(self, cookies, severTime, severDay, widDict, stuInfo)

        FuckDaily.severChan(self, severDay)


if __name__ == '__main__':
    app = FuckDaily()
    app.run()