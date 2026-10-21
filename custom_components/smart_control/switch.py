"""Switch platform for Smart Control Integration."""
from homeassistant.components.mqtt.mixins import MQTTAvailabilityMixin
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 151 relays dynamically."""
    switches = []
    for i in range(1, 152):
        relay_name = f"Relay{i}"
        state_topic = f"esp32/relays/{relay_name}/state"
        command_topic = f"esp32/relays/{relay_name}/set"
        switches.append(SmartControlRelay(relay_name, state_topic, command_topic))
    
    async_add_entities(switches)

class SmartControlRelay(SwitchEntity):
    """Representation of a Smart Control MQTT Relay."""

    def __init__(self, name: str, state_topic: str, command_topic: str):
        self._name = name
        self._attr_name = f"Smart Control {name}"
        self._attr_unique_id = f"smart_control_{name.lower()}"
        self._state_topic = state_topic
        self._command_topic = command_topic
        self._is_on = False
        self._attr_icon = "mdi:power-socket-eu"

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs):
        await self.hass.components.mqtt.async_publish(
            self.hass, self._command_topic, "ON", qos=0, retain=False
        )
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.hass.components.mqtt.async_publish(
            self.hass, self._command_topic, "OFF", qos=0, retain=False
        )
        self._is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Subscribe to MQTT state updates."""
        async def message_received(msg):
            payload = msg.payload
            if payload == "ON":
                self._is_on = True
            elif payload == "OFF":
                self._is_on = False
            self.async_write_ha_state()

        await self.hass.components.mqtt.async_subscribe(
            self._state_topic, message_received
        )
