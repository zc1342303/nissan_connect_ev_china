import logging

from homeassistant.const import (
    STATE_UNKNOWN
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    'battery_soc': {
        'name': '剩余电量',
        'icon': 'hass:battery',
        'unit_of_measurement': '%',
        'attributes': ['last_up_date']
    },
    'recharge_mileage': {
        'name': '续航里程',
        'icon': 'hass:map-marker-distance',
        'unit_of_measurement': 'km',
        'attributes': ['last_up_date']
    },
    'speed': {
        'name': '车速',
        'icon': 'hass:car-speed-limiter',
        'unit_of_measurement': 'km/h',
        'attributes': ['last_up_date']
    },
    'vin': {
        'name': '车架号',
        'icon': 'hass:numeric',
    },
    'last_time': {
        'name': '更新时间',
        'icon': 'hass:update',
    },
    'left_back_door': {
        'name': '左后车门',
        'icon': 'hass:car-door',
    },
    'left_front_door': {
        'name': '左前车门',
        'icon': 'hass:car-door',
    },
    'right_back_door': {
        'name': '右后车门',
        'icon': 'hass:car-door',
    },
    'right_front_door': {
        'name': '右前车门',
        'icon': 'hass:car-door',
    },
    'offline': {
        'name': '掉线',
        'icon': 'hass:help-network-outline',
    },
    'recharge_stat': {
        'name': '充电状态',
        'icon': 'hass:battery-charging-60',
    },
    'recharge_type': {
        'name': '充电类型',
        'icon': 'hass:battery-unknown',
    },
    'car_lock': {
        'name': '锁车',
        'icon': 'hass:lock-outline',
    },
}


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    sensors = []
    coordinator = hass.data[DOMAIN]
    data = coordinator.data

    _LOGGER.debug(data)

    for key in SENSORS.keys():
        if key in data.keys():
            sensors.append(NCSensor(coordinator, key))

    async_add_devices(sensors, True)


class NCBaseSensor(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._unique_id = None

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False


class NCSensor(NCBaseSensor):
    def __init__(self, coordinator, sensor_key):
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._config = SENSORS[self._sensor_key]
        self._attributes = self._config.get("attributes")
        self._coordinator = coordinator
        self._unique_id = f"{DOMAIN}.{sensor_key}"
        self.entity_id = self._unique_id

    def get_value(self, attribute=None):
        try:
            if attribute is None:
                return self._coordinator.data.get(self._sensor_key)
            return self._coordinator.data.get(attribute)
        except KeyError:
            return STATE_UNKNOWN

    @property
    def name(self):
        return self._config.get("name")

    @property
    def state(self):
        return self.get_value()

    @property
    def icon(self):
        return self._config.get("icon")

    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def unit_of_measurement(self):
        return self._config.get("unit_of_measurement")

    @property
    def extra_state_attributes(self):
        attributes = {}
        if self._attributes is not None:
            try:
                for attribute in self._attributes:
                    attributes[attribute] = self.get_value(attribute)
            except KeyError:
                pass
        return attributes
