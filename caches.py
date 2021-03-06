import os
import time
import sys 

datasets = ["example.in", "me_at_the_zoo.in",
            "videos_worth_spreading.in", "trending_today.in", "kittens.in"]
dataset_index = 2 # choose the dataset here
total_requests = 0 # will be used to compute time saved per request
start_time = time.time()

class Video:

    quantity = 0

    def __init__(self, index, size):
        self.is_requested = False
        self.index = index
        self.size = size

    def info(self):
        print("Video", self.index, "of size", self.size)

    @classmethod
    def set_quantity(cls, q):
        if cls.quantity == 0:
            cls.quantity = q
        else:
            print("Error: quantity is already known")

    @classmethod
    def get_quantity(cls):
        print(cls.quantity, "videos available")
        return cls.quantity


class Server:

    def __init__(self, index):
        self.index = index
        self.videos = []
        self.type = "Regular server"

    def add_video(self, vid):
        if type(vid) == Video:
            self.videos.append(vid)
        elif type(vid) == list:
            self.videos += vid

        if self.type == "Cache server":
            if self.free_space - vid.size >= 0:
                self.free_space -= vid.size
                #print("Added video", vid.index, "to cache", self.index,
                #      "Free space remaining:", self.free_space)
            else:
                return 0
                print("Error: no free space on server")

        return 1

    def info(self):
        if len(self.videos) == 0:
            print("Server", self.index, "has no videos")
            return 0
        else:
            print("Server", self.index, "has the following videos:")
            for vid in self.videos:
                print("\t\t", end="")
                vid.info()
            return 1


class Cache(Server):

    quantity = 0
    size = 0

    def __init__(self, index):
        Server.__init__(self, index)
        self.type = "Cache server"
        self.free_space = self.size

    def generate_output_string():
        pass

    @classmethod
    def set_size(cls, size):
        if cls.size == 0:
            cls.size = size
        else:
            print("Error: quantity is already known")

    @classmethod
    def set_quantity(cls, q):
        if cls.quantity == 0:
            cls.quantity = q
        else:
            print("Error: quantity is already known")

    @classmethod
    def get_quantity(cls):
        print(cls.quantity, "caches available")
        return cls.quantity


class Endpoint:

    quantity = 0

    def __init__(self, index, request_descriptions):
        self.index = index
        self.request_descriptions = request_descriptions
        self.requests = []
        self.connections = []

    def add_connection(self, con):
        self.connections.append(con)

    def add_request(self, req):
        self.requests.append(req)

    def info(self):
        if len(self.connections) == 0:
            print("Endpoint", self.index, "has no connections")
            return 0
        elif len(self.requests) == 0:
            print("Endpoint", self.index, "has no requests")
            return 0
        else:
            print("Endpoint", self.index, "has:")
            print("\t1. The following connections:")
            for c in self.connections:
                print("\t\t", end="")
                c.info()
            print("\t2. The following requests:")
            for r in self.requests:
                print("\t\t", end="")
                r.info()
            return 1

    @classmethod
    def set_quantity(cls, q):
        if cls.quantity == 0:
            cls.quantity = q
        else:
            print("Error: quantity is already known")

    @classmethod
    def get_quantity(cls):
        print(cls.quantity, "endpoints present")
        return cls.quantity


class Connection:

    def __init__(self, server, latency):
        self.server = server
        self.latency = latency

    def info(self):
        print("Connection to server", self.server.index,
              "with latency", self.latency)


class Request:

    quantity = 0

    def __init__(self, video, frequency):
        self.video = video
        self.frequency = frequency

    def info(self):
        print(self.frequency, "requests for video", str(self.video.index))

    @classmethod
    def set_quantity(cls, q):
        if cls.quantity == 0:
            cls.quantity = q
        else:
            print("Error: quantity is already known")

    @classmethod
    def get_quantity(cls):
        print(cls.quantity, "request descriptions")
        return cls.quantity

print("Processing dataset", datasets[dataset_index])
sys.stdout.flush()
# split input file into a list of rows
f = []
with open(os.path.join("datasets", datasets[dataset_index])) as input_file:
    f = input_file.read().split('\n')
    f = [n.split(" ") for n in f]

# convert all strings to ints
for i in range(0, len(f)):
    f[i] = [int(n) for n in f[i]]

info = {"videos": f[0][0], "endpoints": f[0][1], "request_d": f[
    0][2], "caches": f[0][3], "cache_size": f[0][4]}

Cache.set_quantity(info["caches"])
Cache.set_size(info["cache_size"])
Video.set_quantity(info["videos"])
Endpoint.set_quantity(info["endpoints"])
Request.set_quantity(info["request_d"])

CACHES = [Cache(i) for i in range(info["caches"])]

VIDEOS = [Video(i, f[1][i]) for i in range(len(f[1]))]

DATACENTER = Server("datacenter")

# Creating list of endpoints
endpoint_info = f[2: len(f) - info["request_d"]]

ENDPOINTS = []

count = 0
endpoint_counter = 0
while count < Request.quantity:

    ENDPOINTS.append(Endpoint(endpoint_counter, endpoint_info[count][1]))
    ENDPOINTS[-1].add_connection(Connection(DATACENTER,
                                            endpoint_info[count][0]))

    num_of_caches = endpoint_info[count][1]
    for c in range(num_of_caches):
        ENDPOINTS[-1].add_connection(Connection(
            CACHES[endpoint_info[count + c + 1][0]], endpoint_info[count + c + 1][1]))
    if count + num_of_caches + 1 >= len(endpoint_info):
        break
    count += num_of_caches + 1
    endpoint_counter += 1

request_info = list(f[-1 * info["request_d"]:])

# Add requests to endpoints while filtering videos that are too big
for req_inf in request_info:
    total_requests += req_inf[2]
    if VIDEOS[req_inf[0]].size <= Cache.size:
        ENDPOINTS[req_inf[1]].add_request(Request(VIDEOS[req_inf[0]], req_inf[2]))

#Get rid of endpoints with no connections to caches
print("Deleting non-relevant endpoints...")
sys.stdout.flush()

ep_index = 0
while ep_index < Endpoint.quantity:
    if len(ENDPOINTS[ep_index].connections) < 2:
        del ENDPOINTS[ep_index]
        Endpoint.quantity -= 1
    else:
        ep_index += 1

print("Deleting non-relevant videos...")
sys.stdout.flush()
# Find all requested videos
for ep in ENDPOINTS:
    for req in ep.requests:
        VIDEOS[req.video.index].is_requested = True

# Get rid of videos that are too big and are not requested
v_index = 0
while v_index < Video.quantity:
    if VIDEOS[v_index].size > Cache.size or VIDEOS[v_index].is_requested == False:
        # print("Deleted", VIDEOS[v_index].size)
        del VIDEOS[v_index]
        Video.quantity -= 1
    else:
        v_index += 1

# Sort cache servers for endpoints by latency OOP
print("Sorting caches by latency...")
sys.stdout.flush()

for ep in ENDPOINTS:
    ep.connections = sorted(ep.connections, key=lambda x: x.latency)

# Calculate importance coefficients for all videos
print("Calculating importance...")
sys.stdout.flush()

USE = {}
COEF_LIST = []  # coef = requests/video size

for ep in ENDPOINTS:
    for req in ep.requests:
        key = req.frequency / req.video.size
        if key not in USE:
            USE[key] = []
        USE[key].append([req.video, ep])
        COEF_LIST.append(key)

COEF_LIST = sorted(set(COEF_LIST), reverse=True)

print("Adding videos to caches...")
sys.stdout.flush()

for coe in COEF_LIST:
    for case in USE[coe]:
        current_video = case[0]
        current_endpoint = case[1]
        for con in current_endpoint.connections:
            cache = con.server
            if cache.type == "Cache server" and current_video.size <= cache.free_space:
                duplicates_found = False
                for vid in cache.videos:
                    if vid == current_video:
                        duplicates_found = True
                        break
                if duplicates_found == False:
                    cache.add_video(current_video)
                break

print("Generating output file...")
sys.stdout.flush()

OUTPUT = []
CAHCES_USED = 0
for cache in CACHES:
    if cache.free_space != Cache.size:
        CAHCES_USED += 1
OUTPUT.append([CAHCES_USED])

for i in range(len(CACHES)):
    if CACHES[i].free_space != Cache.size:
        OUTPUT.append([CACHES[i].index])
        for v in CACHES[i].videos:
            OUTPUT[-1].append(v.index)


with open(datasets[dataset_index] + '_result.txt', 'w') as o:    
    for row in OUTPUT:
        string = ""
        for c in row:
            string += str(c) + " "
        o.write(string[:-1] + "\n")

print("Output is ready")
sys.stdout.flush()

# Compute total time saved
print("Computing score...")
sys.stdout.flush()

total_time_saved = 0
for ep in ENDPOINTS:
    for req in ep.requests:
        for con in ep.connections:
            if req.video in con.server.videos:
                total_time_saved += (ep.connections[-1].latency - con.latency) * req.frequency
                break

score = (total_time_saved / total_requests) * 1000
total_time = time.time() - start_time
print("Score:", str(int(score)))
print("Computation time:", str(int(total_time)))
sys.stdout.flush()

with open(datasets[dataset_index] + '_score.txt', 'w') as o:   
    o.write("Score: " + str(int(score)) + "\n")
    o.write("Computation time: " + str(int(total_time)))
