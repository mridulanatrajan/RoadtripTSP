from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import numpy as np
import random
import math
from gurobipy import *


# Create your views here.

def tsp(request):
    return render(request,'Salesmen/tsp.html',{})

@csrf_exempt
def trip(request):
    out = json.loads(request.body.decode('utf-8'))
    durations = []
    for i in range(0,len(out)):
        durations.append(out[i]["city"+str(i)])
    durm = np.asarray(durations)
    d,totaltime=simulated(durm)  #call to simulated annealing algorithm
    d1,totaltime1=constraints(durm) #call to subtour elimination
    flat = ordering(d,durm)
    print(d,d1)
    print(totaltime,totaltime1)
    flat1=ordering(d1,durm)
    print(flat,flat1)
    if totaltime1<totaltime:
        jslist = json.dumps([{"path":flat1},{"totaltime":totaltime1}])
    elif totaltime1>totaltime:
        jslist = json.dumps([{"path":flat},{"totaltime":totaltime.item()}])
    else:
        jslist = json.dumps([{"path":flat1},{"totaltime":totaltime1}])

    return HttpResponse(jslist)
    

#objective function
def objective(routes,durm):
   distance=0
   for a,b in routes:
       distance+=durm[a][b]
   
   return distance
   
       
#generate initial solution
def initialsolution(row):
   initial=[]
   for i in range(row):
       if i < row-1:
           initial.append([i,i+1])
       if i == row-1:
           initial.append([i,initial[0][0]])
   return initial
   
#swap cities
def swap(route,row):
    city1=random.randrange(row)
    city2=random.randrange(row)
   
    if city1!=city2:
        for l in route:
            if l[0] == city1:
                l[0]='tmp'
            elif l[1] == city1:
                l[1]='tmp'
                
        for l in route:
            if l[0] == city2:
                l[0]=city1
            elif l[1] == city2:
                l[1]=city1
                
        for l in route:
            if l[0]=='tmp':
                l[0]=city2
            elif l[1]=='tmp':
                l[1]=city2
    else:
        swap(route,row)
        
    return route

'''
def simulated(durm):
   row,col=durm.shape
   path=initialsolution(row)
   cost=objective(path,durm)
   T=0.27
   Tmin=0.0001
   alpha=0.9
   while T>Tmin:
       newpath=swap(path,row)
       newcost=objective(newpath,durm)
       deltaE=cost-newcost
       if deltaE<0:
           cost=newcost
           path=newpath
       elif random.random() < math.exp(-deltaE/T):
           cost=newcost
           path=newpath
       
       T=T*alpha
       
   return path,cost
'''

def simulated(durm):
   row,col=durm.shape
   path=initialsolution(row)
   cost=objective(path,durm)
   T=0.27
   Tmin=0.0001
   alpha=0.9
   while T>Tmin:
       newpath=swap(path,row)
       newcost=objective(newpath,durm)
       deltaE=cost-newcost
       if deltaE>0:
           cost=newcost
           path=newpath
       elif random.random() < math.exp(deltaE/T):
           cost=newcost
           path=newpath
       
       T=T*alpha
       
   return path,cost


def ordering(path,durm):
    reorder=[path[0][0],path[0][1]]
    while(len(reorder)!=len(durm)+1):
        for b in path:
            if reorder[-1]==b[0]:
                reorder.extend([b[1]])
            
    return reorder

############################################SUBTOUR ELIMINATION#################################################



def constraints(durm):
    #descision variables
    path=[]
    distance=0
    
    m=Model()
    row,col=durm.shape

    vars=m.addVars(row,col,vtype=GRB.BINARY)

    obj=LinExpr()
    for i in range(row):
        for j in range(col):
            if durm[i,j]!=0:
                obj+=durm[i,j]*vars[i,j]

    m.setObjective(obj,GRB.MINIMIZE)

    #Original Constraints
    edgesum=LinExpr()
    for i in range(row):
        for j in range(col):
            edgesum+=vars[i,j]
    m.addConstr(edgesum,GRB.EQUAL,row)


    #below two constraints are to make sure that there is exactly one edge entering and leaving a node
    for i in range(row):
        entr=LinExpr()
        for j in range(col):
            entr+=vars[i,j]
        m.addConstr(entr,GRB.EQUAL,1)


    for j in range(col):
        leav=LinExpr()
        for i in range(row):
            leav+=vars[i,j]
        m.addConstr(leav,GRB.EQUAL,1)


    #do not count the same node to the same node as an edge
    for i,j in zip(range(row),range(col)):
        same=LinExpr()
        same=vars[i,j]
        m.addConstr(same,GRB.EQUAL,0)

    #Travelling Salesman Main function
    def solveTSP():

        edgelist=[]

        m.optimize()
        sol=m.getAttr('x',vars)

        for edges, presense in sol.iteritems():
            if presense == 1:
                edgelist.append(edges)
         
        tour=[edgelist[0]]
        stour,nodes=subtour(edgelist,tour,edgelist[0],[],[])


        if len(stour)==len(set(nodes)) and len(stour)<row:
            cycle=LinExpr()
            for e in stour:
                cycle+=vars[e[0],e[1]]
            m.addConstr(cycle,GRB.LESS_EQUAL,len(stour)-1)
            return solveTSP()
        else:
            return edgelist,m.objVal
        
        
        


    #determine if there is a subtour and add constraints appropriately
    def subtour(edgelist,tour,selected,nodesvisited,edge):
        nodesvisited.append(selected[0])
        for i in edgelist:
            if i!=selected and i[0]==selected[1]:
                tour.append(i)
                edge+=i
                if i[1] in nodesvisited:
                    break 
                else:
                    subtour(edgelist,tour,i,nodesvisited,edge)            
        return tour,edge
    
    return solveTSP()
    #print("blah blah",path,distance)

