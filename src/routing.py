
# Adjacency group
class Entry:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port


# Routing table of the tracker node
class RoutingTable:
    @classmethod
    def __init__(self):
        self.groups = [[]]

    @classmethod
    def add_group(self,groupList):
        self.groups += [groupList]



    @classmethod
    def load(self,configFile):
        f = open(configFile, "r")
        line = f.readline()

        if line[0] != '#':
            return "Error config file bad structure"

        rt =  RoutingTable()
        groupList = []

        for line in f:
            if line[0]=='#':
                rt.add_group(groupList)
                groupList = []
            else:
                content = line.split(" ")
                groupList += [Entry(content[0],content[1])]

        rt.add_group(groupList)
        f.close()


    @classmethod
    def display(self):
        for group in self.groups:
            for entry in group:
                print(entry.ip + " :: " + entry.port)
