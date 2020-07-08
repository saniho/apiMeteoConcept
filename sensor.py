"""Sensor for my first"""
import logging
from collections import defaultdict
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_CODE,
    ATTR_ATTRIBUTION,
    CONF_SCAN_INTERVAL,
)

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.util import slugify
from homeassistant.util.dt import now, parse_date

_LOGGER = logging.getLogger(__name__)

DOMAIN = "saniho"

ICON = "mdi:package-variant-closed"

SCAN_INTERVAL = timedelta(seconds=1800)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_TOKEN): cv.string,
        vol.Optional(CONF_CODE): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)

class myMeteo:
    def __init__(self, token, insee):
        self._token = token
        self._insee = insee
        pass

    def __pluie(self, aCombienDeTemps):
        pass

    def _update(self):
        # gestion d'un cache pour l'update...ou d'un timer pour eviter trop d'update ?
        # gestion en locale des answer
        import json

        status_counts = defaultdict(int)
        from urllib.request import urlopen
        httpAnswer = urlopen(
            'https://api.meteo-concept.com/api/forecast/nextHours?token=%s&insee=%s&hourly=true' % (self._token, self._insee))
        forecast = json.loads(httpAnswer.read())['forecast']
        return forecast


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the platform."""
    name = config.get(CONF_NAME)
    update_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    token = config.get(CONF_TOKEN)
    _LOGGER.warning(token)
    insee = config.get(CONF_CODE)
    _LOGGER.warning(insee)

    try:
        session = []
    except :
        _LOGGER.exception("Could not run my First Extension")
        return False

    mMeteo = myMeteo( token, insee)
    add_entities([cumulPluieA1h(session, name, update_interval, mMeteo)], True)
    add_entities([probabilitePluieA1h(session, name, update_interval, mMeteo)], True)
    # on va gerer  un element par heure ... maintenant

class cumulPluieA1h(Entity):
    """cumulPluieA1h."""

    def __init__(self, session, name, interval, myMeteo):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._myMeteo = myMeteo
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myMeteo.cumulPluieEstime.1h"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "mm"

    def _update(self):
        """Update device state."""
        forecast = self._myMeteo._update()
        status_counts = defaultdict(int)
        status_counts[0] = forecast[0]['rr10']

        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        self._state = sum(status_counts.values())

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON

class probabilitePluieA1h(Entity):
    """probabilitePluieA1h."""

    def __init__(self, session, name, interval, myMeteo):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._myMeteo = myMeteo
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myMeteo.probabilitePluieEstime.1h"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "%"

    def _update(self):
        """Update device state."""

        forecast = self._myMeteo._update()
        status_counts = defaultdict(int)
        status_counts[0] = forecast[0]['probarain']

        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        self._state = sum(status_counts.values())

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON