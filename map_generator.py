import random
import numpy

map = numpy.full((2, 23, 40), "000")
#                 Z, Y,  X

#LAYER 0
map[0][:] = "024"

#LAYER 1
for i in range(map.shape[1]):
    for n in range(map.shape[2]):
        if random.randint(1,5) == 5:     map[1,i,n] = "0"+str(random.randint(55 , 56))

map[1][0][0:] = "001"   #layer1, line top, X-axis
map[1][-1][0:] = "001"  #layer1, line bottom, X-axis
map[1][0:, 0]  = "001"  #layer1, Line left, Y-axis
map[1][0:, -1] = "001"  #layer1, line right, Y-axis


with open("cmap_data.txt", "w") as data_file:
    for slice in map:
        numpy.savetxt(data_file, slice, fmt='%s')
        numpy.savetxt(data_file, ["#>break<#"], fmt='%s')