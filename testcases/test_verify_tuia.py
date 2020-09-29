import requests
from jsonpath import jsonpath
import unittest
import time
import hashlib
from common.my_logger import log
from common.config import my_config


class TestVerify(unittest.TestCase):
    key = my_config.get("data", "key")

    def setUp(self) -> None:
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
        login_params["sign"] = self.create_sign(login_params, self.key, login_api)
        response = requests.get(url=login_url, params=login_params)
        log.info(login_params)
        log.info(response.json())
        self.sessionid = jsonpath(response.json(), "$..sessionid")[0]
        self.userid = jsonpath(response.json(), "$..userid")[0]

    def test_verify_ad(self):
        confignovelh5_url = "http://m.bbxs8.com/api/getconfignovelh5"
        confignovelh5_api = confignovelh5_url.split("/")[-1]
        confignovelh5_params = {
            "adHost": "m.bbxs1.com",  # 参数化
            "cid": "mk1099",
            "platform": "distribute",
            "s_access": "4G",
            "s_browser": "iphone",
            "s_device_brand": "iPhone",
            "s_device_id": "undefined",  # 参数化（待定）
            "s_os_version": "iOS13.23",
            "s_pid": "H5WEB",
            "s_spid": "3314_csbmtest",  # 参数化
            "sessionid": self.sessionid,
            "t": str(int(time.time() * 1000)),
            "userid": self.userid,
            "version": "3.0.0"
        }
        confignovelh5_params["sign"] = self.create_sign(confignovelh5_params, self.key, confignovelh5_api)
        list5_params = {
            "cids": "csbmtest",  # 参数化
            "did": "16355763",
            "envirs": "browse-common",  # 参数化
            "pids": "4501",  # 待定
            "project": "moka"
        }
        confignovelh5_response = requests.get(url=confignovelh5_url, params=confignovelh5_params)
        flag = jsonpath(confignovelh5_response.json(), "$..useSsp")[0]
        if flag:
            list5_response = requests.get(url="http://svr.ssp.paimei.com/ssp-svr/ssp/list5", params=list5_params)
            ad_id = jsonpath(list5_response.json(), "$..adid")[0]
            third_key = jsonpath(list5_response.json(), "$..thirdKey")[0]
            third_ad_platforms = jsonpath(list5_response.json(), "$..thirdAdPlatforms")[0]
            pv_url = jsonpath(list5_response.json(), "$..pv")[1] + "&did=" + str(list5_params.get("did"))
            pv_response = requests.get(url=pv_url)
            log.info(pv_response.json())
            if third_ad_platforms == "TUIA":
                tuia_params = {
                    "appKey": third_key,  # 参数化
                    "adslotId": ad_id  # 参数化
                }
                tuia_response = requests.get(url="https://engine.seefarger.com/index/serving", params=tuia_params)
                log.info(tuia_response.json())
                self.assertEqual("0", jsonpath(tuia_response.json(), "$..code")[0])
                self.assertEqual(True, jsonpath(tuia_response.json(), "$..success")[0])

    def create_sign(self, param, key, api):
        hashlib_obj = hashlib.md5()
        list_key = list(param.keys())
        list_key.sort()
        str_values = ""
        for i in list_key:
            str_values += param.get(i)
        hashlib_obj.update((str_values + key + api).encode())
        return hashlib_obj.hexdigest().upper()
