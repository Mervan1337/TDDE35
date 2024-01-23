#!/usr/bin/env python
import GuiTextArea, RouterPacket, F
from tabulate import tabulate
from copy import deepcopy

class RouterNode():
    myID = None
    myGUI = None
    sim = None
    costs = None

    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.next_hop = [i for i in range(sim.NUM_NODES)]
        self.costs = deepcopy(costs)
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")
        # Fyller distvector med infinity som startvärde och sätter kända värden
        self.distvector = [[sim.INFINITY] * sim.NUM_NODES for _ in range(sim.NUM_NODES)]
        self.distvector[self.myID] = self.costs
        self.update_neighbour()
    

    # --------------------------------------------------
    #called by the simulator (executed) when a node receives an update from one of its neighbors
    def recvUpdate(self, pkt):              
        src = pkt.sourceid      #id of sending router sending this pkt
        mincost = pkt.mincost   #min cost to node 0 ... 3

        self.distvector[src] = mincost
        old_cost = deepcopy(self.costs)
        self.bellman_ford()

        #check if the cost has been updated
        if self.costs != old_cost:
            self.update_neighbour()

    def update_neighbour(self):
        # Send update to neighbors if the distance vector for router i has changed
        for i in range(self.sim.NUM_NODES):
            if i != self.myID and self.distvector[self.myID][i] != self.sim.INFINITY: 
                new_pkt = RouterPacket.RouterPacket(self.myID, i, self.create_vector(i))
                self.sendUpdate(new_pkt)
            

    def bellman_ford(self):
        costs = [self.sim.INFINITY for _ in range(self.sim.NUM_NODES)]
        costs[self.myID] = 0
        next_hop = [self.myID for _ in range(self.sim.NUM_NODES)]
        for i in range(self.sim.NUM_NODES):
            for j in range(self.sim.NUM_NODES):
                #check if the path from node i to node j through the current node is shorter than the current cost
                if self.distvector[self.myID][i] + self.distvector[i][j] < costs[j]:
                    #update cost with shorter path
                    costs[j] = self.distvector[i][j] + self.distvector[self.myID][i]
                    #determine the next hop based on the shortest path
                    if self.distvector[self.myID][i] == 0:
                        #if the current node is the source, set the next hop to the destination node
                        next_hop[j] = j
                    else:
                        #else set the next hop to the node along the shortest path
                        next_hop[j] = i
        #update
        self.costs = costs
        self.next_hop = next_hop


    def create_vector(self, dest):
        result = []
        #poison reverse
        for i in range(self.sim.NUM_NODES):
            if self.sim.POISONREVERSE and self.next_hop[i] == dest:
                result.append(self.sim.INFINITY)
            else:
                result.append(self.costs[i])
        return result
    



    # --------------------------------------------------
    #only communicate with other routers via the sendUpdate()
    def sendUpdate(self, pkt):
        self.sim.toLayer2(pkt)


    # --------------------------------------------------
    #used for debugging and testing of code, and also for demonstration of your solution to the assignment.
    def printDistanceTable(self):
        self.myGUI.println("Current table for " + str(self.myID) + " at time " + str(self.sim.getClocktime()))
        self.myGUI.println("")
        self.myGUI.println("Distance table:")
        header = ["DST"] + [str(i) for i in range(self.sim.NUM_NODES)]

        table_data = []
        for i in range(self.sim.NUM_NODES):
            temp = [f"nbr {i}"] + self.distvector[i]
            table_data.append(temp)
       
        table = tabulate(table_data, headers=header)
        self.myGUI.println(table)
        self.myGUI.println("")

        self.myGUI.println("Our distance vector and routes:")
        data = [["costs"] + self.costs] + [["route"] + self.next_hop]


        cost_table = tabulate(data, headers=header)
        self.myGUI.println(cost_table)
        self.myGUI.println("")

    # --------------------------------------------------
    #called by the simulator (executed) when the cost of link of a node is about to change
    def updateLinkCost(self, dest, newcost):

        self.distvector[self.myID][dest] = newcost
        old_cost = deepcopy(self.costs)
        self.bellman_ford()

        #check if the cost has been updated
        if self.costs != old_cost:
            self.update_neighbour()

