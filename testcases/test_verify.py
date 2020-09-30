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
from common.text_replace import ConText, data_replace


@ddt
class TestVerify(unittest.TestCase):
    read_excel = ReadExcel(os.path.join(DATA_DIR, "cases_data.xlsx"), "test")
    cases = read_excel.read_data_obj()
    key = my_config.get("data", "key")

    def setUp(self):
        # 参数化处理，将部分需要处理的参数保存为 ConText 类属性
        setattr(ConText, "t", str(int(time.time() * 1000)))
        setattr(ConText, "s_spid", "3314_" + my_config.get("data", "spid"))
        login_url = my_config.get("data", "login_url")
        login_params = {
            "cid": "mk1099",
            "mac": "16QNQ0KJL0946066518",
            "platform": "distribute",
            "s_access": "4G",
            "s_browser": "iphone",
            "s_device_brand": "iPhone",
            "s_device_id": "16QNQ0KJL0946066518",
            "s_os_version": "iOS13.23",
            "s_pid": "H5WEB",
            "s_spid": "mk1099",
            "sex": "1",
            "t": str(int(time.time() * 1000)),
            "version": "3.0.0"
        }
        login_api = login_url.split("/")[-1]
        login_params["sign"] = TestVerify.create_sign(login_params, self.key, login_api)
        response = requests.get(url=login_url, params=login_params)
        sessionid = jsonpath(response.json(), "$..sessionid")[0]
        userid = jsonpath(response.json(), "$..userid")[0]
        # 参数传递处理，将 userid,sessionid 保存为 ConText 类属性
        setattr(ConText, "userid", str(userid))
        setattr(ConText, "sessionid", str(sessionid))

    @data(*cases)
    def test_verify_case(self, case):
        log.info(case.title + "开始")
        getconfiggameh5_url = case.url
        # 截取 url 路径，用于生成 sign
        getconfiggameh5_api = getconfiggameh5_url.split("/")[-1]
        getconfiggameh5_params = eval(data_replace(case.getconfiggameh5_params))
        getconfiggameh5_params["sign"] = TestVerify.create_sign(getconfiggameh5_params, self.key, getconfiggameh5_api)
        getconfiggameh5_method = case.method
        getconfiggameh5_response = requests.request(url=getconfiggameh5_url, params=getconfiggameh5_params,
                                                    method=getconfiggameh5_method)
        log.info(getconfiggameh5_response.json())
        flag = jsonpath(getconfiggameh5_response.json(), "$..useSsp")[0]
        # 开启 ssp 则，继续执行 list5 接口
        if flag:
            list5_url = my_config.get("data", "list5_url")
            list5_params = eval(data_replace(case.list5_params))
            list5_method = case.method
            list5_response = requests.request(url=list5_url, params=list5_params, method=list5_method)
            log.info(jsonpath(list5_response.json(), "$..pmap"))
            # 将pmap回写到excel
            self.read_excel.write_data(case.case_id + 1, 9, str(jsonpath(list5_response.json(), "$..pmap")[0]))
            # PV 上报
            pv_url = jsonpath(list5_response.json(), "$..pv")[1] + "&did=" + getattr(ConText, "userid")
            pv_response = requests.get(url=pv_url)
            log.info(pv_response.json())
            if jsonpath(list5_response.json(), "$..pmap"):
                try:
                    self.assertTrue(jsonpath(list5_response.json(), "$..clist"))
                except AssertionError as e:
                    log.error(e)
                    raise e
                else:
                    pass
        else:
            log.error("未开启SSP")
        log.info(case.title + "结束")
    @staticmethod
    def create_sign(param, key, api):
        hashlib_obj = hashlib.md5()
        list_key = list(param.keys())
        list_key.sort()
        str_values = ""
        for i in list_key:
            str_values += param.get(i)
        hashlib_obj.update((str_values + key + api).encode())
        return hashlib_obj.hexdigest().upper()