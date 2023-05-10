import os
import shutil
import threading
# os.environ["PATH"] = os.environ["PATH"] + ";C:/Users/hakim/repos/sumo-1.14.1/bin/"
# os.environ["SUMO_HOME"] = "C:/Users/hakim/repos/sumo-1.14.1/"


class myThread (threading.Thread):
    def __init__(self, src_files, dirnames, nruns_per_scenario):
        threading.Thread.__init__(self)

        self.src_files = src_files
        self.dirnames = dirnames
        self.nruns_per_scenario = nruns_per_scenario

    def run(self):
        for dirname_ in self.dirnames:
            for sub_folder in range(self.nruns_per_scenario):
                dirname = dirname_ + "/" + str(sub_folder) + "/"

                for fsrc in self.src_files:
                    shutil.copy(fsrc, dirname + "/" + os.path.basename(fsrc))

                # https://sumo.dlr.de/docs/Tools/Trip.html
                os.system(
                    "cd " + dirname + " && netconvert --osm-files map.osm -o test.net.xml "
                                     "-t osmNetconvert.typ.xml --xml-validation never && polyconvert "
                                     "--net-file test.net.xml --osm-files map.osm --type-file typemap.xml "
                                     "-o map.poly.xml --xml-validation never && "
                                     "python randomTrips.py --random -n test.net.xml -r map.rou.xml -o trips.trips.xml "
                                     # "--fringe-factor 1000 --intermediate 5 --validate -p 0.125 -b 0 -e 55 " # generates ~416 vehicles 
                                     "--fringe-factor 1000 --intermediate 5 --validate -p 0.1 -b 0 -e 25 " # generates ~ vehicles 
                                     "--trip-attributes=\"type=\\\"typedist1\\\"\" --additional-file typedistrib1.xml")
                '''
                Key Params Explanations:
                    --random        Each run gets different trips
                    --fringe-factor Increase the weight to initiate vehicles from edges
                    --intermediate  intermediate stops for each vehicles, which increasing the vehicle time before exit 
                    --validate      makes sure the number of routes are valid
                    -b              The time to start the generation of vehicles
                    -e              The time to end the generation of vehicles (sometimes it generates afterwards)
                    -p              the period between vehicles. This is also helps defining the number of vehicles 
                                    where n = (e-b)/2p or p = (e-b)/2n
cmd1: 'netconvert --osm-files map.osm -o test.net.xml -t osmNetconvert.typ.xml --xml-validation never && polyconvert --net-file test.net.xml --osm-files map.osm --type-file typemap.xml -o map.poly.xml --xml-validation never'
250veh/km cmd2: 'python randomTrips.py --random -n test.net.xml -r map.rou.xml -o trips.trips.xml --fringe-factor 1000 --intermediate 5 --validate -p 0.06 -b 0 -e 120 --trip-attributes="type=\"typedist1\"" --additional-file typedistrib1.xml'                                    
450 veh/km cmd2: 'python randomTrips.py --random -n test.net.xml -r map.rou.xml -o trips.trips.xml --intermediate 5 --validate -p 0.01 -b 0 -e 120 --trip-attributes="type=\"typedist1\"" --additional-file typedistrib1.xml'                                    
                '''

if __name__ == '__main__':
    # path = '/media/bassel/Career/toronto_content_selection/toronto'
    output_dataset_path = '/media/bassel/Career/toronto_broadcasting_scores/dataset'
    output_dataset_path = '/media/bassel/Career/toronto_broadcasting_scores/dataset/'
    # path = 'C:/Users/hakim/data/toronto_broadcasting/'
    maps_path = './data'
    maps_path = '/media/bassel/Career/toronto_broadcasting_scores/maps'
    nruns_per_scenario = 1
    # nruns_per_scenario = 12

    if os.path.exists(output_dataset_path):
        shutil.rmtree(output_dataset_path, True)

    os.makedirs(output_dataset_path)

    file_names = os.listdir(maps_path)
    map_file_names = [name for name in file_names if name.find(".osm") != -1]
    base_pos_file_names = [name for name in file_names if name.find(".txt") != -1]
    map_file_names.sort()

    base_name='toronto_'
    rename_ds = False
    base_name=''

    for i in range(len(map_file_names)):
        if rename_ds:
            os.makedirs(output_dataset_path + "/" + base_name + str(i))
        else:
            os.makedirs(output_dataset_path + "/" + base_name + map_file_names[i].replace(".osm", ""))

        for sub_folder in range(nruns_per_scenario):
            if rename_ds:
                dirname = output_dataset_path + "/" + base_name + str(i) + "/" + str(sub_folder) + "/"
            else:
                dirname = output_dataset_path + "/" + base_name + map_file_names[i].replace(".osm", "") + "/" + str(sub_folder) + "/"

            os.makedirs(dirname)

    for i in range(len(map_file_names)):#, base_pos_file_names)):
        map_name =  map_file_names[i]
        base_pos_name = ""

        if len(base_pos_file_names) == len(map_file_names):
            base_pos_name = base_pos_file_names[i]

        for sub_folder in range(nruns_per_scenario):
            if rename_ds:
                dirname = output_dataset_path + "/" + base_name + str(i) + "/" + str(sub_folder) + "/"
            else:
                dirname = output_dataset_path + "/" + base_name + map_file_names[i].replace(".osm", "") + "/" + str(sub_folder) + "/"

            shutil.copy(maps_path + "/" + map_name, dirname + "/map.osm")

            if base_pos_name != "":
                shutil.copy(maps_path + "/" + base_pos_name, dirname + "/basestation_pos.txt")

    src_files = [os.path.dirname(__file__) + '/sumo_files/net.sumo.cfg',
                os.path.dirname(__file__) + '/sumo_files/net2geojson.py',
                os.path.dirname(__file__) + '/sumo_files/osmNetconvert.typ.xml',
                os.path.dirname(__file__) + '/sumo_files/randomTrips.py',
                os.path.dirname(__file__) + '/sumo_files/typemap.xml',
                os.path.dirname(__file__) + '/sumo_files/typedistrib1.xml']

    n_threads = 12
    n = n_threads if n_threads<len(map_file_names) else len(map_file_names)
    block_Size = len(map_file_names)//n
    list_threads = []

    for i in range(n):
        start = i * block_Size
        end = start + block_Size

        if i == n-1:
            end = len(map_file_names)

        print("thread " + str(i) + " launched")

        if rename_ds:
            dirnames = [output_dataset_path + "/" + base_name + str(i) for i in range(start, end)]
        else:
            dirnames = [output_dataset_path + "/" + base_name + map_file_names[i].replace(".osm", "") for i in range(start, end)]

        initialize_maps_thread = myThread(src_files, dirnames, nruns_per_scenario)
        initialize_maps_thread.start()
        list_threads.append(initialize_maps_thread)

    for i in range(n):
        list_threads[i].join()

    print("File Preparation Done! Happy Simulations : )")

