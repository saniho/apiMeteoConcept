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
    def __init__(self, token, insee, _update_interval):
        self._token = token
        self._insee = insee
        self._lastSynchro = None
        self._update_interval = _update_interval
        pass


    def update(self):
        import json
        import datetime

        courant = datetime.datetime.now()
        #_LOGGER.warning("--------------")
        #_LOGGER.warning("tente un update  ? ... %s" %(self._lastSynchro))
        if ( self._lastSynchro == None ) or \
            ( (self._lastSynchro + self._update_interval) < courant ):

            #_LOGGER.warning("tente un update  ? ...")
            #if ( self._lastSynchro != None):
            #    _LOGGER.warning("self._lastSynchro + self._update_interval = %s" %(self._lastSynchro + self._update_interval) )
            #    _LOGGER.warning("courant = %s" %(courant))

            #_LOGGER.warning("update ...")
            from urllib.request import urlopen
            httpAnswer = urlopen(
                'https://api.meteo-concept.com/api/forecast/nextHours?token=%s&insee=%s&hourly=true' % (self._token, self._insee))
            self._forecast = json.loads(httpAnswer.read())['forecast']
            self._lastSynchro = datetime.datetime.now()

            #_LOGGER.warning("update fait, last synchro ... %s " %(self._lastSynchro))
        return self._forecast

    def getPluieADelai(self, duree):
        if duree == "1H":
            return self._forecast[0]['rr10']
        elif duree == "2H":
            return self._forecast[1]['rr10']
        elif duree == "3H":
            return self._forecast[2]['rr10']
        elif duree == "4H":
            return self._forecast[3]['rr10']
        elif duree == "5H":
            return self._forecast[3]['rr10']
        elif duree == "6H":
            return self._forecast[3]['rr10']
        elif duree == "7H":
            return self._forecast[3]['rr10']

    def getProbaPluieDelai(self, duree):
        if duree == "1H":
            return self._forecast[0]['probarain']
        elif duree == "2H":
            return self._forecast[1]['probarain']
        elif duree == "3H":
            return self._forecast[2]['probarain']
        elif duree == "4H":
            return self._forecast[3]['probarain']
        elif duree == "5H":
            return self._forecast[3]['probarain']
        elif duree == "6H":
            return self._forecast[3]['probarain']
        elif duree == "7H":
            return self._forecast[3]['probarain']

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
    for i in [ "1H", "2H", "3H", "4H", "5H", "6H", "7H"]:
        add_entities([cumulPluieAh(session, name, update_interval, mMeteo, insee, i)], True)
        add_entities([probabilitePluieAh(session, name, update_interval, mMeteo, insee, i)], True)
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
        status_counts[0] = self._myMeteo.getPluieADelai( self._delai )

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
        status_counts[0] = self._myMeteo.getProbaPluieDelai(self._delai)

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