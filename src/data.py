
# Tabela quem mantém a informção à cerca de toda a topologia da overlay
class OverlayTable:
    @classmethod
    def __init__(self):
        self.groups = []

    @classmethod
    def add_group(self,ip,groupList):
        self.groups.append({ "node_ip" : ip ,"port" : -1,"neighbours" : groupList})

    def get_port(self,ip):
        for group in self.groups:
            if group["node_ip"] == ip:
                return group["port"]

    def get_neighbours(self,ip):
        neighbours_list = []
        for group in self.groups:
            if group["node_ip"] == ip:
                for entry in group["neighbours"]:
                    neighbours_list.append({ "node_ip" : entry, "port" : self.get_port(entry)})

        return neighbours_list



    def active_node(self,ip,listening_port):
        for group in self.groups:
            if group["node_ip"]==ip:
                group["port"] = listening_port


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
class RoutingTable:

    def __init__(self):
        self.streams = []

    def add_stream(self,source,destination):
        new_stream = Stream(source,destination)
        self.streams.append(new_stream)

    def open_stream(self,source):
        for stream in self.streams:
            if(stream.source==source):
                stream.state = "open"

    def close_stream(self,source):
        for stream in self.streams:
            if(stream.source==source):
                stream.state = "closed"

    def delete_stream(self,source):
        for stream in self.streams:
            if(stream.source==source):
                # Isto funciona?
                self.streams.remove(stream)
