import asyncio
import json
import logging

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
        body = f'api=iov.evnissan.data.selInfo&appCode=nissan_ev&projectType=iov-ev&sign={self._config.get("sign")}&timestamp={self._config.get("timestamp")}&userId={self._config.get("userid")}'
        r = await self._session.post(OVERVIEW_URL, headers=self.headers, data=body, timeout=10)
        if r.status == 200:
            result = json.loads(await r.read())
            if result["msg"] == 'SUCCESS':
                self._info['battery_soc'] = int(result["rows"]["soc"])  # 剩余电量
                self._info['recharge_mileage'] = float(result['rows']['endurKM']) / 10  # 续航里程 * 10
                self._info['speed'] = int(result['rows']['speed'])  # 车速
                self._info['left_back_door'] = 'Open' if result['rows']['lbDoor'] else 'Close'  # 左后车门
                self._info['left_front_door'] = 'Open' if result['rows']['lfDoor'] else 'Close'  # 左前车门
                self._info['right_back_door'] = 'Open' if result['rows']['rbDoor'] else 'Close'  # 右后车门
                self._info['right_front_door'] = 'Open' if result['rows']['rfDoor'] else 'Close'  # 右前车门
                self._info['last_time'] = result['rows']['lastTime']  # 最近更新时间
                self._info['vin'] = result['rows']['vin']  # 车架号
                # "offlineFlag": "0", 是否掉线

            else:
                _LOGGER.warning(body)
                raise InvalidData(f"async_get_overview error: {result['msg']}")
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
