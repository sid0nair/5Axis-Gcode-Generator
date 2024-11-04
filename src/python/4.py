def cube(x,t):
    l=[]
    i=0
    while (i<x):
        
        l.append(printer(('G01',x/2,-x/2,i,0)))
        l.append(printer(('G01',x/2,x/2,i,0)))
        l.append(printer(('G01',-x/2,x/2,i,0)))
        l.append(printer(('G01',-x/2,-x/2,i,0)))
        i=i+t 
    return l

def extru(x,l,h,t):
    g_code = cube(x,t)
    i=0
    g_code.append(printer(('G00',-l/2,-l/2,x,90)))
    while i<=h:
        g_code.append(printer(('G01',x/2,-x/2,i+x,90)))
        g_code.append(printer(('G01',x/2,x/2,i+x,90)))
        g_code.append(printer(('G01',-x/2,x/2,i+x,90)))
        g_code.append(printer(('G01',-x/2,-x/2,i+x,90)))
        i=i+t 
    return g_code

def printer(data):
    result = f"{data[0]} X{data[1]:.4f} Y{data[2]:.4f} Z{data[3]:.4f} U{data[4]:.4f} "
    return(result)          

for i in extru(10,5,5,1):
    print(i)