"""Sensor platform for Smart Control Integration."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate sensors."""
    sensors = [
        SmartControlSensor(
            "Living Room Temperature",
            "esp32/sensors/living_room/temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            "mdi:thermometer"
        ),
        SmartControlSensor(
            "Living Room Humidity",
            "esp32/sensors/living_room/humidity",
            PERCENTAGE,
            SensorDeviceClass.HUMIDITY,
            "mdi:water-percent"
        )
    ]
    async_add_entities(sensors)

class SmartControlSensor(SensorEntity):
    """Representation of a Smart Control MQTT Sensor."""

    def __init__(self, name, topic, unit, device_class, icon):
        self._attr_name = f"Smart Control {name}"
        self._attr_unique_id = f"smart_control_{name.lower().replace(' ', '_')}"
        self._topic = topic
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = icon
        self._attr_native_value = None

    async def async_added_to_hass(self):
        """Subscribe to MQTT state updates."""
        async def message_received(msg):
            try:
                self._attr_native_value = float(msg.payload)
                self.async_write_ha_state()
            except ValueError:
                pass

        await self.hass.components.mqtt.async_subscribe(
            self._topic, message_received
        )
