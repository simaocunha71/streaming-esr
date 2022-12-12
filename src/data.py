from threading import Lock

# Tabela quem mantém a informção à cerca de toda a topologia da overlay
class OverlayTable:
    @classmethod
    def __init__(self):
        self.groups = []
        self.lock = Lock()

    @classmethod
    def add_group(self,ip,groupList):
        self.groups.append({ "node_ip" : ip ,"neighbours" : groupList })

    def get_neighbours(self,ip):
        self.lock.acquire()
        try:
            neighbours_list = []
            for group in self.groups:
                if group["node_ip"] == ip:
                    for entry in group["neighbours"]:
                        neighbours_list.append({ "node_ip" : entry })
            return neighbours_list
        except Exception as e:
            print(e)
        finally:
            self.lock.release()

    @classmethod
    def load(self,configFile):
        f = open(configFile, "r")

        groupList = []
        actual_node = ""
        for line in f:
            line = line.strip()
            if line == "":
                continue
            elif line[0]=='#':
                if groupList != []:
                    self.add_group(actual_node,groupList)
                actual_node = line[1:]
                groupList = []
            else:
                groupList.append(line)

        if groupList != []:
            self.add_group(actual_node,groupList)
        f.close()


    @classmethod
    def display(self):
        for group in  self.groups:
            print("VIZINHOS DE " + group["node_ip"] + ":")
            for entry in group["neighbours"]:
                print(entry)

# Tabela de stream, guarda detalhes de um fluxo de stream partilhar num nodo
class Stream:
    def __init__(self,source,destination):
        self.source = source
        self.destination = destination
        self.state = "closed"



# Table de routing, guarda conjunto de streams num nodo
class StreamsTable:

    def __init__(self):
        self.lock = Lock()
        self.streams = []
        self.status = "closed"

    def is_empty(self):
        self.lock.acquire()
        try:
            return len(self.streams) == 0
        finally:
            self.lock.release()
        

    def stream_table_status(self):
        self.lock.acquire()
        try:
            return self.status
        finally:
            self.lock.release()

    def add_stream(self,source,destination):
        self.lock.acquire()
        try:
            new_stream = Stream(source,destination)
            self.streams.append(new_stream)
        finally:
            self.lock.release()

    def open_stream(self,source):
        self.lock.acquire()
        try:
            for stream in self.streams:
                if(stream.source==source):
                    stream.state = "open"
                    if(self.status != "open"):
                        self.status = "open"
        finally:
            self.lock.release()

    def check_status(self):
        close = True
        for stream in self.streams:
            if(stream.state == "open"):
                close  = False
        if(close):
            self.status = "closed"


    def close_stream(self,source):
        self.lock.acquire()
        try:
            for stream in self.streams:
                if(stream.source==source):
                    stream.state = "closed"
            self.check_status()
        finally:
            self.lock.release()

    def delete_stream(self,source):
        self.lock.acquire()
        try:
            for stream in self.streams:
                if(stream.source==source):
                    self.streams.remove(stream)
            if(self.status != "closed"):
                self.check_status()
        finally:
            self.lock.release()

    def get_streams(self):
        self.lock.acquire()
        try:
            open_entries = []
            for stream in self.streams:
                if(stream.state=="open"):
                    open_entries.append(stream)
            return open_entries
        finally:
            self.lock.release()

class Route:
    def __init__(self,source,saltos,delta):
        self.source = source
        self.saltos = saltos
        self.delta = delta

class RoutingTable:

    def __init__(self):
        self.lock = Lock()
        self.routes = []

    def add_route(self,source,saltos,delta):
        self.lock.acquire()
        try:
            new_route = Route(source,saltos,delta)
            self.routes.append(new_route)
        finally:
            self.lock.release()

    def print(self):
        print("Routing Table:")
        print("Origem------Saltos------Delta")
        for route in self.routes:
            print(str(route.source) + "      " + str(route.saltos) + "      " + str(route.delta))

    def next_jump(self):
        self.lock.acquire()
        try:
            min = self.routes[0].delta
            next_jump = self.routes[0].source
            for route in self.routes:
                if route.delta < min:
                    min = route.delta
                    next_jump = route.source
            return next_jump
        finally:
            self.lock.release()
