from bdp import *

block.size = (7,5)

vert = 'tncsb'
hor = 'wce'

for i,v in enumerate(vert):
    for j,h in enumerate(hor):
        print(v+h)
        fig << block(r"alignment \\ '"+v+h+"'", color='gray!70', alignment=v+h,p=(j*8, i*5.5))

 

