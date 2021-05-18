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

from . import const

DOMAIN = "saniho"

ICON = "mdi:package-variant-closed"

SCAN_INTERVAL = timedelta(seconds=1800)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_TOKEN): cv.string,
        vol.Optional(CONF_CODE): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)

class myMeteo:
    def __init__(self, token, insee, _update_interval):
        self._token = token
        self._insee = insee
        self._lastSynchro = None
        self._update_interval = _update_interval


    def update(self):
        import json
        import datetime

        courant = datetime.datetime.now()
        if ( self._lastSynchro == None ) or \
            ( (self._lastSynchro + self._update_interval) < courant ):

            from urllib.request import urlopen
            httpAnswer = urlopen(
                'https://api.meteo-concept.com/api/forecast/nextHours?token=%s&insee=%s&hourly=true' % (self._token, self._insee))
            self._forecast = json.loads(httpAnswer.read())['forecast']
            self._lastSynchro = datetime.datetime.now()

            _LOGGER.warning("update fait, last synchro ... %s " %(self._lastSynchro))
        return self._forecast

    def getLastSynchro(self):
        return self._lastSynchro

    def _getIndice(self, duree ):
        #_LOGGER.warning("duree getIndice ... *%s* " % (duree))
        monDico =  {
            "1H":0,
            "2H":1,
            "3H":2,
            "4H":3,
            "5H":4,
            "6H":5,
            "7H":6,
            "8H":7,
            "9H":8,
            "10H":9,
            "11H":10,
            "12H":11
        }
        return monDico[ duree ]

    def getPluieADelai(self, duree):
        #_LOGGER.warning("self._forecast ... %s " % (self._forecast))
        #_LOGGER.warning("duree ... *%s* " % (duree))
        #_LOGGER.warning("self._getIndice[duree] ... %s " % (self._getIndice(duree)))
        return self._forecast[self._getIndice(duree)]['rr10']

    def getProbaPluieDelai(self, duree):
        return self._forecast[self._getIndice(duree)]['probarain']

    def getTemperatureADelai(self, duree):
        return self._forecast[self._getIndice(duree)]['temp2m']

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

    mMeteo = myMeteo( token, insee, update_interval)
    mMeteo.update()
    for i in [ "1H", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "11H", "12H"]:
        add_entities([cumulPluieAh(session, name, update_interval, mMeteo, insee, i)], True)
        add_entities([probabilitePluieAh(session, name, update_interval, mMeteo, insee, i)], True)
    add_entities([lastSynchro(session, name, update_interval, mMeteo, insee )], True)

    # on va gerer  un element par heure ... maintenant

class cumulPluieAh(Entity):
    """cumulPluieA1h."""

    def __init__(self, session, name, interval, myMeteo, insee, delai):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._myMeteo = myMeteo
        self._insee = insee
        self._delai = delai
        self._interval = interval
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myMeteo.%s.cumulPluieEstime.%s" %(self._insee, self._delai)

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
        self._myMeteo.update()
        status_counts = defaultdict(int)
        delai = self._myMeteo.getPluieADelai( self._delai )

        status_counts["Delai"] = delai
        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        self._state = "%s" %delai

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON

class temperatureAh(Entity):
    """cumulPluieA1h."""

    def __init__(self, session, name, interval, myMeteo, insee, delai):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._myMeteo = myMeteo
        self._insee = insee
        self._delai = delai
        self._interval = interval
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myMeteo.%s.temperatureEstimee.%s" %(self._insee, self._delai)

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
        self._myMeteo.update()
        status_counts = defaultdict(int)
        temperature = self._myMeteo.getTemperatureADelai( self._delai )

        status_counts["temperature"] = temperature
        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        self._state = "%s" %temperature

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON

class probabilitePluieAh(Entity):
    """probabilitePluieA1h."""

    def __init__(self, session, name, interval, myMeteo, insee, delai):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._myMeteo = myMeteo
        self._insee = insee
        self._delai = delai
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myMeteo.%s.probabilitePluieEstime.%s" %(self._insee, self._delai)

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

        self._myMeteo.update()
        status_counts = defaultdict(int)
        pluie = self._myMeteo.getProbaPluieDelai(self._delai)
        status_counts["Pluie"] = pluie
        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        self._state = "%s" %pluie

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON
    

class lastSynchro(Entity):
    """probabilitePluieA1h."""

    def __init__(self, session, name, interval, myMeteo, insee):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._myMeteo = myMeteo
        self._insee = insee
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myMeteo.%s.derniereSynchro" %(self._insee)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return ""

    def _update(self):
        """Update device state."""

        status_counts = defaultdict(int)
        lastSynchro = self._myMeteo.getLastSynchro()

        status_counts["LastSynchro"] = lastSynchro
        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        self._state = lastSynchro.strftime("%d-%b-%Y (%H:%M:%S)")

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON