#!/usr/bin/python
# -*- coding: utf-8 -*-

from apts import *

my_equipment = Equipment()

sky_watcher = "SW"

my_equipment.register(equipment.Camera(23.5, 15.6, 6000, 4000, "Nikon"))
my_equipment.register(equipment.Telescope(150, 750, sky_watcher, t2_output = True))
my_equipment.register(equipment.Barlow(2, sky_watcher, t2_output = True))
my_equipment.register(equipment.Eyepiece(25, sky_watcher))
my_equipment.register(equipment.Eyepiece(10, sky_watcher))

my_place = Place(lat=50.1637973, lon=19.7855169, name="Zelków")
my_observation = Observation(my_place, my_equipment)

if my_observation.weather_is_good():
  notify = Notify('lpozarlik@gmail.com')
  notify.send(my_observation)
