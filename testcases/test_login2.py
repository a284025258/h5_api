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
        if case.interface == "login":
            login_url = case.url
            login_params = eval(case.params.replace("#t#", str(int(time.time() * 1000))))
            login_api = login_url.split("/")[-1]
            login_params["sign"] = self.create_sign(login_params, self.key, login_api)
            log.info(login_params)
            login_method = case.method
            login_response = requests.request(url=login_url, params=login_params, method=login_method)
            log.info(login_response.json())

    def create_sign(self, param, key, api):
        hashlib_obj = hashlib.md5()
        list_key = list(param.keys())
        list_key.sort()
        str_values = ""
        for i in list_key:
            str_values += param.get(i)
        hashlib_obj.update((str_values + key + api).encode())
        return hashlib_obj.hexdigest().upper()