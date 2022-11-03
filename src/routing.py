
# Routing table of the tracker node
class RoutingTable:
    @classmethod
    def __init__(self):
        self.groups = []

    @classmethod
    def add_group(self,node,groupList):
        self.groups.append((node,groupList))



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
        for (node,group) in self.groups:
            print("VIZINHOS DE " + node + ":")
            for entry in group:
                print(entry)

rt = RoutingTable()
rt.load("config.txt")
rt.display()