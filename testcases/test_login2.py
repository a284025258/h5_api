import unittest
from lib.ddt import ddt, data
import requests
import time
from jsonpath import jsonpath
from common.read_excel import ReadExcel
from common.constant import DATA_DIR
import os
from common.config import my_config
from common.my_logger import log
import hashlib
from common.text_replace import ConText

@ddt
class TestLogin2(unittest.TestCase):
    read_excel = ReadExcel(os.path.join(DATA_DIR, "cases_data.xlsx"), "test")
    cases = read_excel.read_data_obj()
    key = my_config.get("data", "key")

    # def setUp(self):
    #     login_url = my_config.get("data", "login_url")
    #     login_params = {
    #         "cid": "mk1099",
    #         "mac": "16QNQ0KJL0946066518",
    #         "platform": "distribute",
    #         "s_access": "4G",
    #         "s_browser": "iphone",
    #         "s_device_brand": "iPhone",
    #         "s_device_id": "16QNQ0KJL0946066518",
    #         "s_os_version": "iOS13.23",
    #         "s_pid": "H5WEB",
    #         "s_spid": "mk1099",
    #         "sex": "1",
    #         "t": str(int(time.time() * 1000)),
    #         "version": "3.0.0"
    #     }
    #     login_api = login_url.split("/")[-1]
    #     login_params["sign"] = self.create_sign(login_params, self.key, login_api)
    #     response = requests.get(url=login_url, params=login_params)
    #     self.sessionid = jsonpath(response.json(), "$..sessionid")[0]
    #     self.userid = jsonpath(response.json(), "$..userid")[0]

    @data(*cases)
    def test_verify_case(self, case):
        # 执行登录接口 获取 sessionid 及 userid
        if case.interface == "login":
            login_url = case.url
            login_params = eval(case.params.replace("#t#", str(int(time.time() * 1000))))
            login_api = login_url.split("/")[-1]
            login_params["sign"] = self.create_sign(login_params, self.key, login_api)
            login_method = case.method
            login_response = requests.request(url=login_url, params=login_params, method=login_method)
            userid = jsonpath(login_response.json(), "$..userid")[0]
            sessionid = jsonpath(login_response.json(), "$..sessionid")[0]
            setattr(ConText, "userid", str(userid))
            setattr(ConText, "sessionid", str(sessionid))
            log.info(login_response.json())
        # 执行 getconfiggameh5 接口 判断是否 开启 ssp
        if case.interface == "getconfiggameh5":
            getconfiggameh5_url = case.url
            getconfiggameh5_api = getconfiggameh5_url.split("/")[-1]
            getconfiggameh5_params = case.params.replace("#t#", str(int(time.time() * 1000)))
            getconfiggameh5_params = getconfiggameh5_params.replace("#s_spid#", "3314_" + my_config.get("data", "s_spid"))
            getconfiggameh5_params = getconfiggameh5_params.replace("#sessionid#", getattr(ConText, "sessionid"))
            getconfiggameh5_params = getconfiggameh5_params.replace("#userid#", getattr(ConText, "userid"))
            getconfiggameh5_params = eval(getconfiggameh5_params)
            getconfiggameh5_params["sign"] = self.create_sign(getconfiggameh5_params, self.key,getconfiggameh5_api)
            getconfiggameh5_method = case.method
            getconfiggameh5_response = requests.request(url=getconfiggameh5_url, params=getconfiggameh5_params, method=getconfiggameh5_method)
            log.info(getconfiggameh5_response.json())
            flag = jsonpath(getconfiggameh5_response.json(), "$..useSsp")[0]
            setattr(ConText, "flag", flag)
        # 开启 ssp 则，继续执行 list5 接口
        if case.interface == "list5" and getattr(ConText, "flag"):
            list5_url = case.url
            list5_api = list5_url.split("/")[-1]
            list5_params = case.params.replace("#s_spid#", my_config.get("data", "s_spid"))
            list5_params = list5_params.replace("#userid#", getattr(ConText, "userid"))
            list5_params = eval(list5_params)
            list5_method = case.method
            list5_response = requests.request(url=list5_url, params=list5_params, method=list5_method)
            log.info(list5_response.json())
            if jsonpath(list5_response.json(), "$..pmap"):
                self.assertTrue(jsonpath(list5_response.json(), "$..clist"))

    def create_sign(self, param, key, api):
        hashlib_obj = hashlib.md5()
        list_key = list(param.keys())
        list_key.sort()
        str_values = ""
        for i in list_key:
            str_values += param.get(i)
        hashlib_obj.update((str_values + key + api).encode())
        return hashlib_obj.hexdigest().upper()