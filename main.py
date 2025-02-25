''' 
Title: Determining Boundary Parcels   
     
'''

from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfilename
# from win32api import GetSystemMetrics
from tkinter import messagebox
import shapefile
from shapely.geometry import shape
from shapely.geometry import polygon
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math


def setSelectfile():
    filename=askopenfilename()
    e1.insert(0,filename)

def angle_between(p1, p2):
    x1=p1[0]
    y1=p1[1]
    x2=p2[0]
    y2=p2[1]
    c=math.atan2((x2-x1),(y2-y1))
    d=math.degrees(c)
    if d<0:
        d=d+360
    return d 

def get_object_id_from_parcel_no(parcel_no, rec_dict):
    return_id=1
    for record in rec_dict.values():
        
        if record.record[2] == parcel_no:
            return_id = record.record[0]
    return return_id

show_box_list = list()
scroll_bar_list = list()

def deleteListBoxes():   
    for lists in show_box_list:
        lists.pack_forget()
    for sbar in scroll_bar_list:
        sbar.pack_forget()

def getEWNSparcel():
        east=[]
        west=[]
        north=[]
        south=[]
              
        deleteListBoxes()

        sbar1 = Scrollbar(right_frame)
        sbar2 = Scrollbar(right_frame)
        sbar3 = Scrollbar(right_frame)
        sbar4 = Scrollbar(right_frame)
        
        listbox1 = Listbox(master=right_frame, yscrollcommand=sbar1.set)
        listbox2 = Listbox(master=right_frame, yscrollcommand=sbar2.set)
        listbox3 = Listbox(master=right_frame, yscrollcommand=sbar3.set)
        listbox4 = Listbox(master=right_frame, yscrollcommand=sbar4.set)
        
        show_box_list.append(listbox1)
        show_box_list.append(listbox2)
        show_box_list.append(listbox3)
        show_box_list.append(listbox4)
        
        scroll_bar_list.append(sbar1)
        scroll_bar_list.append(sbar2)
        scroll_bar_list.append(sbar3)
        scroll_bar_list.append(sbar4)
        
        dk=list(centroidDict.keys())
        print(centroidDict.keys())
        print(dk)
        dv=list(centroidDict.values())
        input_parcel=eval(e2.get())

        for i in dv:
            originParcelCentroid=centroidDict[input_parcel]
            angle=angle_between(originParcelCentroid,i)
            if centroidDict[input_parcel]==i:
                pass
            elif (angle>=45 and angle<135):
                east.append(dk[dv.index(i)])
            elif (angle>=135 and angle<215):
                south.append(dk[dv.index(i)])
                
            elif (angle>=215 and angle<315):
                west.append(dk[dv.index(i)])
                
            else:
                north.append(dk[dv.index(i)])
        
        listbox1.insert(END, "East")
        listbox1.insert(END, " ")
        for i in east:         
            listbox1.insert(END, str(i))
            
        listbox2.insert(END, "West") 
        listbox2.insert(END, " ")
        for i in west:   
            listbox2.insert(END, str(i))
            
        listbox3.insert(END, "North") 
        listbox3.insert(END, " ")
        for i in north:
            listbox3.insert(END, str(i))
            
        listbox4.insert(END, "South") 
        listbox4.insert(END, " ")
        for i in south: 
            listbox4.insert(END, str(i))
            
        listbox1.pack(side=LEFT, fill=BOTH)
        sbar1.pack(side=LEFT, fill=Y)
        listbox2.pack(side=LEFT, fill=BOTH)
        sbar2.pack(side=LEFT, fill=Y)
        listbox3.pack(side=LEFT, fill=BOTH)
        sbar3.pack(side=LEFT, fill=Y)
        listbox4.pack(side=LEFT, fill=BOTH)
        sbar4.pack(side=LEFT, fill=Y)
    
        sbar1.config(command=listbox1.yview)
        sbar2.config(command=listbox2.yview)
        sbar3.config(command=listbox3.yview)
        sbar4.config(command=listbox4.yview)
        
centroidDict=dict()
canvasID = 0
def ShowResult():
    sf=shapefile.Reader(str(e1.get()))
    input_parcel=eval(e2.get())
    global centroidDict, canvas, canvasID  
    
    deleteListBoxes()
    recordDict = dict()
    parcelPlot=dict()   
    inputTestList=list()
    
    for rec in sf.shapeRecords():
        inputTestList.append(rec.record[2])             
    if (input_parcel not in inputTestList):
        messagebox.showinfo("Error","Invalid Parcel Number")    

    for rec in sf.shapeRecords():        
        recordDict[rec.record[0]]= rec        
    
    k = get_object_id_from_parcel_no(input_parcel, recordDict)
    
    myRecord = recordDict[k]    
    parcelPlot[k] = myRecord.shape.points
    
    objects_touching_this = [] # list of object ids
    
    for other_key in list(recordDict.keys()):
        if other_key == k:
            continue

        other_rec = recordDict[other_key]

        my_shape = shape(myRecord.shape.__geo_interface__)
        
        
        other_shape = shape(other_rec.shape.__geo_interface__)
        if my_shape.intersects(other_shape):
            parcelPlot[other_key] = other_rec.shape.points
            objects_touching_this.append(other_rec.record[2])
 
                 
    coordCollection={}    
    points_collection = []
    for obj in parcelPlot.keys():
        for rec in recordDict.keys():
            if obj==rec:
                
                requiredRecord=recordDict[obj]
                reqRecParcel=recordDict[obj].record[2]
                coordCollection[reqRecParcel]=polygon.Polygon(requiredRecord.shape.points)
                points_collection.append(requiredRecord.shape.points) 
            
            
    
    boundary = gpd.GeoSeries(coordCollection)
    
    fig = Figure(figsize=(6,6))
      
    plt.ylabel("Northing", fontsize=14)
    plt.xlabel("Easting", fontsize=14)
    
    centroidDict.clear()
    a = fig.add_subplot(111)
    for each_shape in points_collection:
        x_s = []
        y_s = []
        
        new_xes= [tup[0] for tup in each_shape]
        new_yes= [tup[1] for tup in each_shape]
        
        x_s.extend(new_xes)
        y_s.extend(new_yes)
        a.plot(x_s, y_s)
        
    for i, geo in boundary.centroid.items():
        
        # a.annotate(s=i, xy=[geo.x, geo.y], color="black")
        a.annotate(text=i, xy=[geo.x, geo.y], color="black")
        #ax.annotate(s=i, xy=[geo.x, geo.y], color="black")
        centroidDict[i]=(geo.x, geo.y)
    
    if canvasID != 0:
        canvas.get_tk_widget().pack_forget()
    canvasID += 1
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()
    
 
root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
print(f"Screen width: {width}, Screen height: {height}")

# width=GetSystemMetrics(0)
# height=GetSystemMetrics(1)
w=str(width)
h=str(height)
root.configure(width=w,height=h,bg="green")
root.title("Determining Boundary Parcel")
v=StringVar()
left_frame = Frame(root, width=200, height=400,bg='skyblue')
left_frame.grid(row=0, column=0, padx=10, pady=5)
right_frame = Frame(root, width=650, height=400, bg='lightgrey')
right_frame.grid(row=0, column=1, padx=10, pady=5)

fig = Figure(figsize=(6,6))
canvas = FigureCanvasTkAgg(fig, master=right_frame)

tool_bar = Frame(left_frame, width=180, height=185)
toolbar=Frame(left_frame, width=180, height=185)
tool_bar.grid(row=2, column=0, padx=5, pady=5)
toolbar.grid(row=10, column=0, padx=5, pady=20)

Label(left_frame, text="Input").grid(row=0, column=0, padx=5, pady=5, ipadx=10)
Label(tool_bar, text="Select ShapeFile (.zip)", relief=RAISED).grid(row=0, column=0, padx=5, pady=3, ipadx=10) 
e1 = Entry(tool_bar,textvariable=v)
e1.grid(row = 1, column =0)

Button(tool_bar, text="Browse", command=setSelectfile).grid(row=2, column=0, padx=5, pady=5)
Label(tool_bar, text="Enter Parcel Number", relief=RAISED).grid(row=3, column=0, padx=5, pady=3, ipadx=10) 

e2 = Entry(tool_bar)

e2.grid(row=4,column=0)
Button(tool_bar, text="Show", command=ShowResult).grid(row=5, column=0, pady=4, ipadx=10)
Button(tool_bar, text="Quit", command=root.destroy).grid(row=6, column=0, pady=4, ipadx=10)
Button(toolbar, text="Display Parcel Direction", command=getEWNSparcel).grid(row=6, column=0, pady=4, ipadx=10)


Label(toolbar, text="Output").grid(row=0, column=0, padx=5, pady=5)

root.mainloop()