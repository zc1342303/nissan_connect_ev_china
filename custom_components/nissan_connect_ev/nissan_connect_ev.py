import asyncio
import json
import logging
import time

_LOGGER = logging.getLogger(__name__)

OVERVIEW_URL = 'https://nvitapp.venucia.com/iov_gw/api'


class AuthFailed(Exception):
    pass


class InvalidData(Exception):
    pass


class NCData:
    headers = {
        "Host": "nvitapp.venucia.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Accept": "application/json",
        "User-Agent": "ri chan zhi lianEV/1.1.9 (iPhone; iOS 16.4.1; Scale/3.00)"
                      "NetType/WIFI Language/zh_CN",
        "Accept-Language": "zh-Hans-CN;q=1, en-CN;q=0.9",
        "Referer": "https://nvitapp.venucia.com",
        "Content-Length": "140"
    }

    def __init__(self, session, config: dict):
        self._session = session
        self._config = config
        self._info = {}

    async def async_get_overview(self):
        """获取概览信息"""
        body = f'api=iov.evnissan.data.selInfo&appCode=nissan_ev&projectType=iov-ev&sign={self._config.get("sign")}&timestamp={int(time.time())}&userId={self._config.get("userid")}'
        r = await self._session.post(OVERVIEW_URL, headers=self.headers, body=body, timeout=10)
        if r.status == 200:
            result = json.loads(await r.read())
            print(result)
            if result["status"] == 0:
                self._info['battery_soc'] = result["rows"]["soc"]  # 剩余电量
            else:
                raise InvalidData(f"get_balance error:{result['msg']}")
        else:
            raise InvalidData(f"overview response status_code = {r.status_code}")

    async def async_get_data(self):
        """refresh data"""
        self._info = {}

        # await self.async_get_token()
        tasks = [
            self.async_get_overview(),
        ]
        await asyncio.wait(tasks)
        _LOGGER.debug(f"Data {self._info}")
        return self._info
