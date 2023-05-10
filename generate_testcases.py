import json
import math

import numpy as np

from math_utils import euclidean_distance
from vehicle_info import Vehicle


def update_vehicle_pos(vehicles, deltaTime):
    for vehicle in vehicles:
        velocity = [vehicle.speed * math.sin(vehicle.orientation_angle_degree*math.pi/180.0), \
                   vehicle.speed * math.cos(vehicle.orientation_angle_degree*math.pi/180.0)]
        vehicle._center[0] += velocity[0]*deltaTime
        vehicle._pos[0] += velocity[0]*deltaTime
        vehicle._center[1] += velocity[1]*deltaTime
        vehicle._pos[1] += velocity[1]*deltaTime


def update_vehicle_perceptions(avs, navs):
    ret = {}

    for av in avs:
        for nav in navs:
            if euclidean_distance(av._center, nav._center) <= av.viewing_range:
                if av.vehicle_id in ret:
                    ret[av.vehicle_id].append(nav.vehicle_id)
                else:
                    ret[av.vehicle_id] = [nav.vehicle_id]

    return ret


def generateTestCase1(save_dir):
    vehicles = [Vehicle("A", 150, 360), Vehicle("B", 150, 360),
                    Vehicle("X", 0, 0)]

    for i in range(600):
        if i == 0:
            vehicles[0]._center = np.array([0, 0, 0], dtype="float")
            vehicles[0]._pos = np.array([0, 0, 0], dtype="float")
            vehicles[0]._speed = 10
            vehicles[0]._acc = 0
            vehicles[0]._orientation_ang_degree = 0

            vehicles[1]._center = np.array([200, 0, 0], dtype="float")
            vehicles[1]._pos = np.array([200, 0, 0])
            vehicles[1]._speed = 1
            vehicles[1]._acc = 0
            vehicles[1]._orientation_ang_degree = 0

            vehicles[2]._center = np.array([75, 0, 0], dtype="float")
            vehicles[2]._pos = np.array([75, 0, 0], dtype="float")
            vehicles[2]._speed = 5
            vehicles[2]._acc = 0
            vehicles[2]._orientation_ang_degree = 0
        else:
            deltaTime = 0.1
            update_vehicle_pos(vehicles, deltaTime)

        perception = update_vehicle_perceptions(vehicles[0:2], vehicles[2:])

        data = {
            "perception": perception,
            "avs": {"A":vehicles[0].toJSON(), "B":vehicles[1].toJSON()},
            "navs": {"X" : vehicles[2].toJSON()},
            "scores": {"A":["B", 1/euclidean_distance(vehicles[1].get_pos(), vehicles[2].get_pos()), "X", 1],
                       "B":["A", 1/euclidean_distance(vehicles[0].get_pos(), vehicles[2].get_pos()), "X", 1]}
        }

        json_filename = f"{save_dir}/state_{i+1}.json"

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    generateTestCase1("/media/bassel/Career/toronto_broadcasting_scores/testcases/1/")