"""
Understanding GIS: Assessment 2
@author [11161619]

An Implementation Weighted Redistribution Algorithm (Huck et al. 2015)
"""
# import the time library
from time import time

# set start time
start_time = time()    # NO CODE ABOVE HERE

from geopandas import read_file, GeoSeries
from rasterio import open as rio_open
from rasterio.plot import show as rio_show
from matplotlib.pyplot import subplots, savefig
from numpy import zeros
from sys import exit
from numpy.random import uniform
from shapely.geometry import Point, box
from math import sqrt, pi, floor, ceil
from numpy import column_stack
from skimage.draw import disk
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.lines import Line2D


#function to calculate the likelihood radius
def likelihood_radius(admin, s):
   
    return(sqrt((admin.area*s)/pi))


#function definition for spatial ambiguity
def spatial_ambiguity(row, column, outputSurface, dem, radius):
   
    #convert the radius to pixels
    radius_px = int(radius/dem.res[0])
   
    #create a disk and get the row and column values of all the pixels in it
    for r, c in column_stack(disk((row,column), radius_px)):
       
        #if we go too far, or go off the edge of the data, stop looping
        if  not 0 <= r < dem.height or not 0 <= c < dem.width:
            break
       
        #convert the locations from image space to coordinate space
        x0,y0 = dem.xy(row,column)
        x,y = dem.xy(r,c)
       
        #update the new value in the disk at this location
        outputSurface[r,c] = outputSurface[r,c] + 1 - sqrt((x0-x)*(x0-x)+(y0-y)*(y0-y))/radius
           
    return(outputSurface)

   
#function definition for weighted redistribution
def weighted_redistribution(sample_number, s, pointData, administrativeAreas, weightingSurface, dem):
   
    #create a new 'band' of raster data the same size
    outputSurface = zeros(weightingSurface.shape)
   
    #loop through all the administrative regions at this level
    for admin in administrativeAreas.geometry:
       
        #get the bounds of admin
        minx, miny, maxx, maxy = admin.bounds
       
        #get the points inside admin
        points = pointData.loc[pointData.within(admin)]
       
        #loop through the points
        for p in points.geometry:
           
            #set max_value variable to 0 which will eventually store the max weight
            max_value = 0
           
            #initiate count to keep track of the random locations generated
            count = 0
           
            #while loop to make sure w random points are generated
            while (count<=w):
               
                #get random points in admin
                x = uniform(low=minx, high=maxx)
                y = uniform(low=miny, high=maxy)

               
                #check if the x and y are within admin
                if Point(x,y).within(admin):
                   
                    #convert x and y to image space
                    r,c = dem.index(x,y)
                   
                    #update the count
                    count = count+1
                   
                    #get the maximum value of the weighting surface for the x and y
                    if weightingSurface[r,c] > max_value:
                       
                        #store the maximum value and its image space coordinates
                        max_value = weightingSurface[r,c]
                        row = r
                        column = c
                   
            #calculate the likelihood radius
            radius = likelihood_radius(admin,s)
           
            #get the spatial ambiguity
            outputSurface = spatial_ambiguity(row, column, outputSurface, dem, radius)
           
           
    return(outputSurface)


#get the influence of the weighting surface
w = 20

#get the level of spatial ambiguity
s = 0.01

#use try statement to catch exceptions
try:
   
    #read the data stored in in tweets database and store it in pointData
    pointData = read_file("./data/level3-tweets-subset.shp")

    #read the administrative areas data and store it in administrativeAreas
    administrativeAreas = read_file("./data/gm-districts.shp")

#exception for no file
except:
   
    print("Sorry,there is no such file in the path")
    exit()

#get the projection string for British National Grid
proj = "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 +units=m +no_defs +type=crs"

#convert the datasets to the same crs
pointData = pointData.to_crs(proj)
administrativeAreas = administrativeAreas.to_crs(proj)

#use try statement to catch exceptions
try:
   
    # open the weighting surface raster dataset
    with rio_open("./data/100m_pop_2019.tif") as dem:
       
        # read the data out of band 1 in the dataset
        weightingSurface = dem.read(1)
       
        outputSurface = weighted_redistribution(w, s, pointData, administrativeAreas, weightingSurface, dem)
       
        #plot the dataset
        fig, my_ax = subplots(1, 1, figsize=(16, 10))
       
        #set title for the plot
        my_ax.set(title="Weighted Redistribution of Tweets within Greater Manchester")
        my_ax.axis('off')
   
        #add the DEM
        rio_show(
            outputSurface,
            ax=my_ax,
            transform = dem.transform,
            cmap= 'magma'
            )
       
       
        #to create a mask layer
        minx, miny, maxx, maxy = administrativeAreas.total_bounds                  
        gm_box = box(minx, miny, maxx, maxy)
   
        #get the difference between greater manchester and the bounding box
        for admin in administrativeAreas.geometry:
   
            gm_box = gm_box.difference(admin)
       
        #plot the mask layer
        GeoSeries(gm_box, crs=dem.crs).plot(ax = my_ax, color = 'white' ,
                                            alpha=1, edgecolor = 'white',
                                            linewidths = 1)
   
        #add colourbar
        fig.colorbar(ScalarMappable(norm=Normalize(vmin=floor(outputSurface.min()),
                                                   vmax=ceil(outputSurface.max())),
                                                   cmap='magma'), ax=my_ax, pad=0.02)
   
        #add north arrow
        x, y, arrow_length = 0.02, 0.99, 0.1
   
        my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
   
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
   
            ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)
   
     
   
        #add scalebar
        my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower right"))
   
        # add legend for the map
        my_ax.legend(handles=[Line2D([0], [0], marker = None, color='w',
                                     label=f'Influence of Weight: {w}\nLevel of Spatial Ambiguity: {s}',
                                     markerfacecolor='black', markersize=8)], loc='lower left')
       
        #save the figure
        savefig('./out/manchester_tweets.png', bbox_inches='tight')
   

#exception for no file
except Exception as e:
    print(e)
    raise
         
# report runtime
print(f"completed in: {time() - start_time} seconds")    # NO CODE BELOW HERE