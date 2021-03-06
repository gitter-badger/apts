import ephem
import pytz

from dateutil import tz

from .weather import Weather

class Place(ephem.Observer):
  def __init__(self, lat, lon, name="", elevation=300, *args):
    ephem.Observer.__init__(self, *args)
    self.lat = str(lat)
    self.lon = str(lon)
    self.name = name
    self.elevation = elevation
    # Sun
    self.sun = ephem.Sun()
    self.sun.compute(self)
    # Moon
    self.moon = ephem.Moon()
    self.moon.compute(self)

    self.weather = Weather(lat, lon)
    self.local_timezone = tz.gettz(self.weather.local_timezone)

  def _next_setting_time(self, obj):
    return self.next_setting(obj).datetime().replace(tzinfo=pytz.UTC).astimezone(self.local_timezone)

  def _next_rising_time(self, obj):
    return self.next_rising(obj).datetime().replace(tzinfo=pytz.UTC).astimezone(self.local_timezone)

  def sunset_time(self):
    return self._next_setting_time(self.sun)

  def sunrise_time(self):
    return self._next_rising_time(self.sun)

  def moonset_time(self):
    return self._next_setting_time(self.moon)

  def moonrise_time(self):
    return self._next_rising_time(self.moon)

