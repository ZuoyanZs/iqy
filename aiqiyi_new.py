import urllib
from time import sleep, time
from random import randint, choice
from json import dumps
from hashlib import md5 as md5Encode
from string import digits, ascii_lowercase, ascii_uppercase
from sys import exit, stdout
from os import environ, system
from re import findall
import pymysql
import requests
from requests import Session, get, post
from fake_useragent import UserAgent
import hashlib

def connect_db():
    '''
    连接数据库，并返回连接对象

    :return: 数据库连接对象
    :rtype: pymysql.connections.Connection
    '''
    conn = pymysql.connect(
        host='123.56.162.xxx',
        user='xxx',
        password='xxx',
        database='xxx',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn
def sha1_hash(data: str) -> bytes:
    '''
    将字符串进行 SHA1 散列处理，并返回散列值

    :param data: 待处理的字符串
    :type data: str
    :return: 该字符串的 SHA1 散列值
    :rtype: bytes
    '''
    return hashlib.sha1(data.encode('utf-8')).digest()

def generate_device_id(steamid_sha1_hash: bytes) -> str:
    '''
    将 SHA1 散列值转换为设备 ID

    :param steamid_sha1_hash: SHA1 散列值
    :type steamid_sha1_hash: bytes
    :return: 设备 ID
    :rtype: str
    '''
    h = steamid_sha1_hash.hex()
    return f"{h[:8]}{h[8:12]}{h[12:16]}{h[16:20]}{h[20:32]}"

def drive_id(drive: str) -> str:
    '''
    根据指定的驱动器名称生成设备 ID

    :param drive: 驱动器名称
    :type drive: str
    :return: 设备 ID
    :rtype: str
    '''
    steamid_sha1_hash = sha1_hash(drive)
    device_id = generate_device_id(steamid_sha1_hash)
    return device_id




def query_data():
    '''
    查询数据库并返回结果

    :return: 查询结果
    :rtype: list[dict]
    '''
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            query = "SELECT p00001, dfp, name FROM ai WHERE state = 1"
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        conn.close()

def update_data(update_query):
    '''
    更新数据库数据

    :param update_query: 更新数据的 SQL 查询语句
    :type update_query: str
    '''
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(update_query)
            conn.commit()
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        conn.close()
class Iqiyi:
    def __init__(self, ck, dfp):
        self.ck = ck
        self.session = Session()
        self.user_agent = UserAgent().chrome
        self.headers = {
            "User-Agent": self.user_agent,
            "Cookie": f"P00001={self.ck}",
            "Content-Type": "application/json"
        }
        self.dfp = dfp
        self.uid = ""
        self.msg = ""
        self.user_info = ""
        self.sleep_await = environ.get("sleep_await") if environ.get("sleep_await") else 1

    """工具"""

    def req(self, url, req_method="GET", body=None):
        try:
            if req_method.upper() == "GET":
                return self.session.get(url, headers=self.headers, params=body).json()
            elif req_method.upper() == "POST":
                return self.session.post(url, headers=self.headers, data=dumps(body)).json()
            elif req_method.upper() == "OTHER":
                self.session.get(url, headers=self.headers, params=dumps(body))
            else:
                print("您当前使用的请求方式有误,请检查")
        except Exception as e:
            print(f"请求发送失败,异常信息：{e}")
            return {}
    def timestamp(self, short=False):
        if (short):
            return int(time())
        return int(time() * 1000)

    def md5(self, str):
        m = md5Encode(str.encode(encoding='utf-8'))
        return m.hexdigest()

    def uuid(self, num, upper=False):
        str = ''
        if upper:
            for i in range(num):
                str += choice(digits + ascii_lowercase + ascii_uppercase)
        else:
            for i in range(num):
                str += choice(digits + ascii_lowercase)
        return str

    def print_now(self, content):
        print(content)
        stdout.flush()

    def get_dfp_params(self):
        get_params_url = "https://api.lomoruirui.com/iqiyi/get_dfp"
        data = get(get_params_url).json()
        return data

    def get_dfp(self):
        body = self.get_dfp_params()
        url = "https://cook.iqiyi.com/security/dfp_pcw/sign"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "1059",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "cook.iqiyi.com",
            "Origin": "https://www.iqiyi.com",
            "Pragma": "no-cache",
            "Referer": "https://www.iqiyi.com/",
            "sec-ch-ua": f"\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"{body['data']['sv']}\", \"Google Chrome\";v=\"{body['data']['sv']}\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.user_agent
        }
        data = post(url, headers=headers, data=body["data"]["body"]).json()
        self.dfp = data["result"]["dfp"]
        self.print_now(self.dfp)

    def get_userinfo(self):
        url = f"https://tc.vip.iqiyi.com/growthAgency/v2/growth-aggregation?messageId={self.qyid}&platform=97ae2982356f69d8&P00001={self.ck}&responseNodes=duration%2Cgrowth%2Cupgrade%2CviewTime%2CgrowthAnnualCard&_={self.timestamp()}"
        data = self.req(url)
        msg = data['data']['growth']
        info = data['data']['user']
        # print(data)
        try:
            self.user_info = f"查询成功: 到期时间{msg['deadline']}\t当前等级为{msg['level']}\n\t今日获得成长值{msg['todayGrowthValue']}\t总成长值{msg['growthvalue']}\t距离下一等级还差{msg['distance']}成长值"
            self.print_now(self.user_info)
            update_data(f"UPDATE ai SET name = '{info['nickname']}', level = {info['level']}, vipdayt='{msg['deadline']}', grows = {msg['growthvalue']} WHERE p00001 = '{iqy_ck}'")
        except:
            self.user_info = f"查询失败,未获取到用户信息"

    """获取用户id"""

    def getUid(self):
        url = f'https://passport.iqiyi.com/apis/user/info.action?authcookie={self.ck}&fields=userinfo%2Cqiyi_vip&timeout=15000'
        data = self.req(url)
        if data.get("code") == 'A00000':
            self.uid = data['data']['userinfo']['pru']
        else:
            self.print_now("请求api失败 最大可能是cookie失效了 也可能是网络问题")
            self.tgpush("爱奇艺每日任务: 请求api失败 最大可能是cookie失效了 也可能是网络问题")
            exit(0)

    def get_watch_time(self):
        url = "https://tc.vip.iqiyi.com/growthAgency/watch-film-duration"
        data = self.req(url)
        watch_time = data['data']['viewtime']['time']
        return watch_time

    def get_sign(self):
        self.qyid = self.md5(self.uuid(16))
        time_stamp = self.timestamp()
        if self.uid == "":
            self.print_now("获取用户id失败 可能为cookie设置错误或者网络异常,请重试或者检查cookie")
            exit(0)
        data = f'agentType=1|agentversion=1|appKey=basic_pcw|authCookie={self.ck}|qyid={self.qyid}|task_code=natural_month_sign|timestamp={time_stamp}|typeCode=point|userId={self.uid}|UKobMjDMsDoScuWOfp6F'
        url = f'https://community.iqiyi.com/openApi/task/execute?agentType=1&agentversion=1&appKey=basic_pcw&authCookie={self.ck}&qyid={self.qyid}&sign={self.md5(data)}&task_code=natural_month_sign&timestamp={time_stamp}&typeCode=point&userId={self.uid}'
        return url

    def getUrl(self, Time, dfp):
        return f'https://msg.qy.net/b?u=f600a23f03c26507f5482e6828cfc6c5&pu={self.uid}&p1=1_10_101&v=5.2.66&ce={self.uuid(32)}&de=1616773143.1639632721.1639653680.29&c1=2&ve={self.uuid(32)}&ht=0&pt={randint(1000000000, 9999999999) / 1000000}&isdm=0&duby=0&ra=5&clt=&ps2=DIRECT&ps3=&ps4=&br=mozilla%2F5.0%20(windows%20nt%2010.0%3B%20win64%3B%20x64)%20applewebkit%2F537.36%20(khtml%2C%20like%20gecko)%20chrome%2F96.0.4664.110%20safari%2F537.36&mod=cn_s&purl=https%3A%2F%2Fwww.iqiyi.com%2Fv_1eldg8u3r08.html%3Fvfrm%3Dpcw_home%26vfrmblk%3D712211_cainizaizhui%26vfrmrst%3D712211_cainizaizhui_image1%26r_area%3Drec_you_like%26r_source%3D62%2540128%26bkt%3DMBA_PW_T3_53%26e%3Db3ec4e6c74812510c7719f7ecc8fbb0f%26stype%3D2&tmplt=2&ptid=01010031010000000000&os=window&nu=0&vfm=&coop=&ispre=0&videotp=0&drm=&plyrv=&rfr=https%3A%2F%2Fwww.iqiyi.com%2F&fatherid={randint(1000000000000000, 9999999999999999)}&stauto=1&algot=abr_v12-rl&vvfrom=&vfrmtp=1&pagev=playpage_adv_xb&engt=2&ldt=1&krv=1.1.85&wtmk=0&duration={randint(1000000, 9999999)}&bkt=&e=&stype=&r_area=&r_source=&s4={randint(100000, 999999)}_dianshiju_tbrb_image2&abtest=1707_B%2C1550_B&s3={randint(100000, 999999)}_dianshiju_tbrb&vbr={randint(100000, 999999)}&mft=0&ra1=2&wint=3&s2=pcw_home&bw=10&ntwk=18&dl={randint(10, 999)}.27999999999997&rn=0.{randint(1000000000000000, 9999999999999999)}&dfp={dfp}&stime={self.timestamp()}&r={randint(1000000000000000, 9999999999999999)}&hu=1&t=2&tm={Time}&_={self.timestamp()}'

    def sign(self):
        url = self.get_sign()
        body = {
            "natural_month_sign": {
                "taskCode": "iQIYI_mofhr",
                "agentType": 1,
                "agentversion": 1,
                "authCookie": self.ck,
                "qyid": self.qyid,
                "verticalCode": "iQIYI",
                "dfp":self.dfp

            }
        }
        data = self.req(url, "post", body)
        # print(data)
        if data.get('code') == 'A00000':
            self.print_now(f"签到执行成功, {data['data']['msg']}")
        else:
            self.print_now("签到失败，原因可能是签到接口又又又又改了")

    def dailyTask(self):
        taskcodeList = {
            "freeGetVip": "浏览会员兑换活动",
            "GetReward": "逛领福利频道",
            'b6e688905d4e7184': "浏览生活福利",
            'a7f02e895ccbf416': "看看热b榜",
            '8ba31f70013989a8': "每日观影成就"}
        for taskcode in taskcodeList:
            # 领任务
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/joinTask?P00001={self.ck}&taskCode={taskcode}&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn'
            if self.req(url)['code'] == 'A00000':
                # print(f'领取{taskcodeList[taskcode]}任务成功')
                sleep(10)
            # 完成任务
            url = f'https://tc.vip.iqiyi.com/taskCenter/task/notify?taskCode={taskcode}&P00001={self.ck}&platform=97ae2982356f69d8&lang=cn&bizSource=component_browse_timing_tasks&_={self.timestamp()}'
            if self.req(url)['code'] == 'A00000':
                # print(f'完成{taskcodeList[taskcode]}任务成功')
                sleep(2)
            # 领取奖励
            # url = f'https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?P00001={self.ck}&taskCode={taskcode}&dfp={self.dfp}&platform=b6c13e26323c537d&lang=zh_CN&app_lm=cn&deviceID={self.md5(self.uuid(8))}&token=&multiReward=1&fv=bed99b2cf5722bfe'
            url = f"https://tc.vip.iqiyi.com/taskCenter/task/getTaskRewards?P00001={self.ck}&taskCode={taskcode}&lang=zh_CN&platform=b2f2d9af351b8603"
            try:
                price = self.req(url)['dataNew'][0]["value"]
                self.print_now(f"领取{taskcodeList[taskcode]}任务奖励成功, 获得{price}点成长值")
            except:
                self.print_now(f"领取{taskcodeList[taskcode]}任务奖励可能出错了 也可能没出错 只是你今天跑了第二次")
            sleep(2)


    def start(self):
        self.print_now("正在执行刷观影时长脚本 为减少风控 本过程运行时间较长 大概10分钟")
        totalTime = self.get_watch_time()
        if totalTime >= 7200:
            self.print_now(f"你的账号今日观影时长大于2小时 不执行刷观影时长")
            return
        for i in range(180):
            Time = randint(60, 120)
            url = self.getUrl(Time, self.dfp)
            self.req(url, 'other')
            totalTime += Time
            sleep(randint(2, 3))
            if i % 20 == 3:
                self.print_now(f"现在已经刷到了{totalTime}秒, 数据同步有延迟, 仅供参考")
            if totalTime >= 7800:
                break

    def getTimes(self):
        url = "https://pcell.iqiyi.com/lotto/queryTimes"

        querystring = {"P00001": self.ck,
                       "dfp": self.dfp,
                       "qyid": self.qyid,
                       "deviceID": drive_id(self.qyid)
            , "version": "15.1.1", "agentType": "12",
                       "platform": "bb35a104d95490f6", "ptid": "02030031010000000000", "fv": "afc0b50ed49e732d",
                       "source": "afc0b50ed49e732d", "_": self.timestamp(), "vipType": "1",
                       "actCode": "92164d9ef47d9dff"}

        headers = {
            "Origin": "https://vip.iqiyi.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": self.user_agent,
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Referer": "https://vip.iqiyi.com/",
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        # print(response.json())
        return response.json()['data']['times']

    def build_querystring(self):
        # 构建查询字符串参数
        return {
            "P00001": self.ck,
            "dfp": self.dfp,
            "qyid": self.qyid, "deviceID": self.qyid,
            "version": "15.1.1", "agentType": "12", "platform": "bb35a104d95490f6",
            "ptid": "02030031010000000000", "fv": "afc0b50ed49e732d", "source": "afc0b50ed49e732d",
            "_": "1711265469107", "vipType": "1", "lotteryType": "2", "actCode": "0k9GkUcjqqj4tne8",
            "freeLotteryNum": "3",
            "extendParams": "{\"appIds\":\"iqiyi_pt_vip_iphone_video_autorenew_12m_348yuan_v2\",\"supportSk2Identity\":true,\"testMode\":\"0\",\"iosSystemVersion\":\"16.0.2\",\"bundleId\":\"com.qiyi.iphone4\"}"}

    def build_headers(self):
        # 构建请求头
        return {
            "Host": "act.vip.iqiyi.com",
            "Origin": "https://vip.iqiyi.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 IqiyiApp/iqiyi IqiyiVersion/15.1.1  IqiyiPlatform/2_22_221 WebVersion/QYWebContainer QYStyleModel/(light)",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Referer": "https://vip.iqiyi.com/",
        }
    def lottery(self):
        url = "https://act.vip.iqiyi.com/shake-api/lottery"
        querystring = self.build_querystring()
        headers = self.build_headers()
        response = requests.request("GET", url, headers=headers, params=querystring)

        print(response.text)

    def send(self):
        url = "https://i.vip.iqiyi.com/rights/transfer/present"

        payload = {
            "P00001": self.ck,
            "vipType": "1",
            "days": "30",
            "appVersion": "15.1.1",
            "dfp": self.dfp,
            "agentType": "12",
            "qyid": self.qyid,
            "qc5": self.qyid,
            "platform": "bb35a104d95490f3"
        }
        encoded_payload = urllib.parse.urlencode(payload)

        headers = {
            "Host": "i.vip.iqiyi.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://vip.iqiyi.com",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "Referer": "https://vip.iqiyi.com/",
            "Content-Length": str(len(encoded_payload)),
            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
        }

        response = requests.post(url, data=encoded_payload, headers=headers)

        print(response.text)
    def main(self):
        if get_iqiyi_dfp:
            self.get_dfp()
        self.getUid()
        self.get_sign()
        self.start()
        sleep(2)
        times = self.getTimes()
        if times >= 3:
            sleep(1)
            self.lottery()
        else: print('今天免费的抽奖次数没有了~ GG')
        self.sign()
        self.dailyTask()
        self.print_now(
            f"任务已经执行完成,10s后展现详情信息 左魇冲冲冲v2.10")
        if int(self.sleep_await) == 1:
            sleep(10)
        self.get_userinfo()


if __name__ == '__main__':
    results = query_data()
    for result in results:
        iqiyi_dfp = result['dfp']
        name = result['name']
        if name is not None:
            print("正在运行的账号是" + name)
        iqy_ck = environ.get("iqy_ck") if environ.get("iqy_ck") else result['p00001']
        get_iqiyi_dfp = environ.get("get_iqiyi_dfp") if environ.get("get_iqiyi_dfp") else False

        if iqy_ck == "":
            print("ck为空，请检查")
            exit(0)
        if "__dfp" in iqy_ck:
            iqiyi_dfp = findall(r"__dfp=(.*?)(;|$)", iqy_ck)[0][0]
            iqiyi_dfp = iqiyi_dfp.split("@")[0]
        if "P00001" in iqy_ck:
            iqy_ck = findall(r"P00001=(.*?)(;|$)", iqy_ck)[0][0]
        if iqiyi_dfp == "":
            iqiyi_dfp = environ.get("iqiyi_dfp") if environ.get(
                "iqiyi_dfp") else "e1c4bbb223f96743af8402aa6379dda541a640017ada7fccbce0f326e01be40742"

        try:
            iqiyi = Iqiyi(iqy_ck, iqiyi_dfp)
            iqiyi.main()
            update_data(f"UPDATE ai SET state = 2 WHERE p00001 = '{iqy_ck}' ")
        except:
            print("失效或错误，运行下一个")
            update_data(f"UPDATE ai SET state = 4 WHERE p00001 = '{iqy_ck}' ")
