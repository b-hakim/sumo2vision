import glob
import multiprocessing
import os
import time
from ast import literal_eval
from enum import Enum
from sumo_visual_scenario import Simulation
import pickle


class RunSimulationProcess(multiprocessing.Process):
    def __init__(self, map, cv2x_percentage, fov, view_range, tot_num_vehicles, id, time_threshold,
                 perception_probability=1.0, estimate_detection_error=False, use_saved_seed=False, save_gnss=False,
                 noise_distance=0, repeat=False, cont_prob=False, avg_speed_meter_per_sec=40000 / 3600, timestamp=1,
                 save_scores = False):
        # multiprocessing.Process.__init__(self)
        super(RunSimulationProcess, self).__init__()

        if type(map) != list:
            sub_dirs = os.listdir(map)
            sub_dirs.sort()
            self.traffics = [os.path.join(map, dirname) for dirname in sub_dirs]
        else:
            self.traffics = map

        self.cv2x_percentage, self.fov, self.view_range, \
        self.tot_num_vehicles, self.perception_probability = cv2x_percentage, fov, view_range, \
                                                                           tot_num_vehicles, perception_probability
        self.use_saved_seed = use_saved_seed
        self.sim_id = id
        self.time_threshold = time_threshold
        self.estimate_detection_error = estimate_detection_error
        self.save_gnss = save_gnss
        self.noise_distance = noise_distance
        self.repeat = repeat
        self.cont_prob = cont_prob
        self.avg_speed_meter_per_sec = avg_speed_meter_per_sec
        self.timestamp = timestamp
        self.save_scores = save_scores

    def run(self):
        print(f"Simulation Thread {str(self.sim_id)} started with a batchsize={len(self.traffics)} ")
        tot_time_start = time.time()

        for traffic in self.traffics:  # toronto_'i'/'j'
            sc_time_start = time.time()
            hyper_params = {}
            hyper_params['scenario_path'] = os.path.join(traffic, "test.net.xml")
            hyper_params['scenario_map'] = os.path.join(traffic, "net.sumo.cfg")
            hyper_params['scenario_polys'] = os.path.join(traffic, "map.poly.xml")
            hyper_params["cv2x_N"] = self.cv2x_percentage
            hyper_params["fov"] = self.fov
            hyper_params["view_range"] = self.view_range
            hyper_params['tot_num_vehicles'] = self.tot_num_vehicles
            hyper_params['time_threshold'] = self.time_threshold
            hyper_params['save_visual'] = False
            hyper_params['perception_probability'] = self.perception_probability
            hyper_params["estimate_detection_error"] = self.estimate_detection_error
            hyper_params["save_gnss"] = self.save_gnss
            hyper_params["noise_distance"] = self.noise_distance
            hyper_params["continous_probability"] = self.cont_prob
            hyper_params["avg_speed_meter_per_sec"] = self.avg_speed_meter_per_sec
            hyper_params["timestamps"] = self.timestamp
            hyper_params["save_scores"] = self.save_scores

            with open(os.path.join(traffic,"basestation_pos.txt"), 'r') as fr:
                hyper_params["base_station_position"] = literal_eval(fr.readline())

            if hyper_params["timestamps"] == 1:
                state_path = os.path.join(traffic, "saved_state",
                                 "state_" + str(hyper_params['cv2x_N'])
                                 + "_" + str(hyper_params['fov'])
                                 + "_" + str(hyper_params["view_range"])
                                 + "_" + str(hyper_params["tot_num_vehicles"])
                                 + "_" + str(hyper_params['time_threshold'])
                                 + "_" + str(hyper_params['perception_probability'])
                                 + ("_ede" if hyper_params["estimate_detection_error"] else "_nede")
                                 + "_" + str(hyper_params["noise_distance"])
                                 + ("_egps" if hyper_params["noise_distance"] != 0 else "")
                                 + ("_cont_prob" if hyper_params["continous_probability"] else "_discont_prob")
                                 + ".pkl")
            else:
                state_path = os.path.join(traffic, "saved_state",
                                             "state_" + str(hyper_params['cv2x_N'])
                                             + "_" + str(hyper_params['fov'])
                                             + "_" + str(hyper_params["view_range"])
                                             + "_" + str(hyper_params["tot_num_vehicles"])
                                             + "_" + str(hyper_params['time_threshold'])
                                             + "_" + str(hyper_params['perception_probability'])
                                             + ("_ede" if hyper_params["estimate_detection_error"] else "_nede")
                                             + "_" + str(hyper_params["noise_distance"])
                                             + ("_egps" if hyper_params["noise_distance"] != 0 else "")
                                             + ("_cont_prob" if hyper_params[
                                                 "continous_probability"] else "_discont_prob")
                                             + f"_{hyper_params['timestamps']}'"
                                             + ".json")

            if os.path.isfile(state_path) and not self.repeat:
                continue


            print(f"Scenario: {traffic[traffic.index('toronto_'):]} started")

            sim = Simulation(hyper_params, str(self.sim_id)+"_"+os.path.basename(traffic))
            sim.run(self.use_saved_seed)

            print(f"Scenario {traffic[traffic.index('toronto_'):]} ended with {time.time()-sc_time_start} seconds")

        print(f"Simulation Thread {str(self.sim_id)} ended with {time.time()-tot_time_start} seconds")


def run_simulation(base_dir, cv2x_percentage, fov, view_range, tot_num_vehicles,
                   perception_probability=1, estimate_detection_error=False, use_saved_seed=False, save_gnss=False,
                   noise_distance=0, repeat=False, cont_prob=False, avg_speed_meter_per_sec=40000/3600, timestamp=1,
                   save_score=False):
    n_scenarios = 3
    s = time.time()

    for i in range(n_scenarios):
        print(f"Scenario: toronto_{i}")
        run_simulation_one_scenario(base_dir, cv2x_percentage, fov, view_range,
                                    tot_num_vehicles, i, perception_probability, estimate_detection_error,
                                    use_saved_seed, save_gnss, noise_distance, repeat, cont_prob,
                                    avg_speed_meter_per_sec, timestamp, save_score)

        if i != n_scenarios-1:
            print("#######################################################################################################")

    print(f"Scenario toronto_0 - toronto_2 took {time.time() - s} seconds")
    print("#######################################################################################################\n")


def run_simulation_one_scenario(base_dir, cv2x_percentage, fov, view_range, tot_num_vehicles,
                                scenario_num, perception_probability, estimate_detection_error,
                                use_saved_seed=False, save_gnss=False, noise_distance=0, repeat=False, cont_prob=False,
                                avg_speed_meter_per_sec=40000 / 3600, timestamp=1, save_score=False):
    time_threshold = 10
    n_threads = 12
    path = f"{base_dir}/toronto_{scenario_num}/"
    maps = os.listdir(path)
    maps = [path + map for map in maps if os.path.isdir(path+map)]
    maps.sort(key=lambda x:int(x.split('/')[-1]))

    if not repeat:
        filtered_maps = []
        for traffic in maps:
            scenario_path = os.path.join(traffic, "test.net.xml")
            state_path = ""

            if timestamp == 1:
                state_path = os.path.join(os.path.dirname(scenario_path), "saved_state",
                             "state_" + str(cv2x_percentage)
                             + "_" + str(fov)
                             + "_" + str(view_range)
                             + "_" + str(tot_num_vehicles)
                             + "_" + str(time_threshold)
                             + "_" + str(perception_probability)
                             + ("_ede" if estimate_detection_error else "_nede")
                             + "_" + str(noise_distance)
                             + ("_egps" if noise_distance != 0 else "")
                             + ("_cont_prob" if cont_prob else "_discont_prob")
                             + ".pkl")
            else:
                state_path = os.path.join(os.path.dirname(scenario_path), "saved_state",
                                          "state_" + str(cv2x_percentage)
                                          + "_" + str(fov)
                                          + "_" + str(view_range)
                                          + "_" + str(tot_num_vehicles)
                                          + "_" + str(time_threshold)
                                          + "_" + str(perception_probability)
                                          + ("_ede" if estimate_detection_error else "_nede")
                                          + "_" + str(noise_distance)
                                          + ("_egps" if noise_distance != 0 else "")
                                          + ("_cont_prob" if cont_prob else "_discont_prob")
                                          +f"_{timestamp}"
                                          + ".json")

            if not os.path.isfile(state_path): # and not os.path.isfile(state_path):
                filtered_maps.append(traffic)

        maps = filtered_maps

    if len(maps) == 0:
        print("No maps to do in this scenario! Going to the next scenario : )")
        return

    n = n_threads if n_threads<len(maps) else len(maps)
    block_size = len(maps)//n

    list_threads = []

    for i in range(n_threads):
        start = i * block_size
        end = start + block_size

        if i == n-1:
            end = len(maps)

        # print(maps[i])
        simulation_thread = RunSimulationProcess(maps[start:end], cv2x_percentage=cv2x_percentage, fov=fov,
                                                 view_range=view_range,
                                                 tot_num_vehicles=tot_num_vehicles, id=i, time_threshold=time_threshold,
                                                 perception_probability=perception_probability,
                                                 estimate_detection_error=estimate_detection_error,
                                                 use_saved_seed=use_saved_seed, save_gnss=save_gnss,
                                                 noise_distance=noise_distance, repeat=repeat, cont_prob=cont_prob,
                                                 avg_speed_meter_per_sec= avg_speed_meter_per_sec, timestamp=timestamp,
                                                 save_scores=save_score)

        simulation_thread.start()
        list_threads.append(simulation_thread)

    max_block_size = (len(maps) - block_size*(len(list_threads)-1)) # length of the last block
    max_block_size = max(block_size, max_block_size)
    # timeout = 300 * 60 * max_block_size
    timeout = 55000

    if timeout < 60:
        print("timeout was", timeout)
        timeout = 60

    print(f"Gonna wait {timeout} seconds for all threads")
    start_time = time.time()
    use_timeout = True

    while True:
        if use_timeout:
            time_taken = time.time() - start_time
            remaining_time = timeout - time_taken

            is_alive = False

            print("Waking up!")

            for i in range(n):
                if list_threads[i].is_alive():
                    is_alive = True
                    print(f"Thread {i} is alive!")
                else:
                    list_threads[i].join(0)
                    list_threads[i].terminate()
                    print(f"Thread {i} finished!")
                    # break

            if not is_alive:
                break

            if remaining_time < 0:
                print("Timeout! Killing remaining threads. . .")
                for i in range(n):
                    try:
                        list_threads[i].join(1)
                        list_threads[i].terminate()
                        print(f"Thread {i} killed")
                    except:
                        print(f"error ending thread {i}")

                break

            # print(f"Waiting threads, sleep {remaining_time} sec. . .")
            print(f"Waiting threads, sleep 1 min. . .")
            time.sleep(60)
            # time.sleep(remaining_time)
        else:
            for i in range(n):
                list_threads[i].join()
                list_threads[i].terminate()
                print(f"Thread {i} finished!")
            break
    cmd = 'pkill sumo'
    os.system(cmd)
    os.system(cmd)



if __name__ == '__main__':
    ####################################  Normal Density  #######################################
    min_num_vehicles = 100
    base_dir = "/media/bassel/Career/toronto_broadcasting/"
    avg_speed_sec = 10
    ####################################  High Density  #########################################
    # min_num_vehicles = 400
    # base_dir = "/media/bassel/Career/toronto_content_selection/toronto_dense"
    # avg_speed_sec = 10
    #############################################################################################
    # delete_all_results = True
    delete_all_results = False

    # delete all results
    if delete_all_results:
        answer = input("Are you sure to delete ALL the results.txt and maps.png??")
        if answer == 'y' or answer == 'yes':
            n_scenarios = 10

            for i in range(n_scenarios):
                # path = f"/media/bassel/Entertainment/sumo_traffic/sumo_map/toronto_gps/toronto/toronto_{i}/"
                path = os.path.join(base_dir, f"toronto_{i}/")

                maps = os.listdir(path)
                maps = [path + map for map in maps]
                maps.sort(key=lambda x: int(x.split('/')[-1]))

                for p in maps:
                    # paths = glob.glob(p + "/result*.txt")
                    # for p2 in paths:
                    #     os.remove(p2)
                    paths = glob.glob(p + "/map*.png")

                    for p2 in paths:
                        os.remove(p2)
                    # paths = glob.glob(p + "/GNSS*.pkl")
                    # for p2 in paths:
                    #     os.remove(p2)

    start_time = time.time()

    run_simulation(base_dir=base_dir,
                   cv2x_percentage=0.65, fov=360, view_range=37.5, tot_num_vehicles=min_num_vehicles,
                   perception_probability=1, estimate_detection_error=False, use_saved_seed=False,
                   repeat=False, save_gnss=False, noise_distance=0, cont_prob=False,
                   avg_speed_meter_per_sec=avg_speed_sec, timestamp=int(10*60*1), save_score=False)
    print("*******************************************************************************************")
    end_time = time.time()

    ###########################################   Test Scenario   #############################################
    # s = time.time()
    # run_simulation_one_scenario(cv2x_percentage=0.65, fov=120, view_range=75, num_RBs=90, tot_num_vehicles=100,
    #                             scenario_num=0, repeat=True)
    # e = time.time()
    # print(f"Done #1 cv2x_percentage=0.25, fov=120, view_range=75, num_RBs=75, tot_num_vehicles=100, total_time={e-s}")
    ###########################################################################################################

    print("time taken:",end_time-start_time)

    print("All Simulations are done! Happy Integrating 9: )")
