"""
@author: Daniel Martinez Martin
"""


from multiprocessing import Process, Lock, Semaphore, Value, Array
import random

NPROD = 10
N = 5# número de elementos que produce cada productor
K = NPROD * N  # tamaño de la lista compartida
NInd=3 #numero de elemtnos que tendra el buffer limitado correspondiente a cada productor
       #este servira para ver cual de los huecos de la lista es un -2


def producer(storage, index, empty,non_empty, mutex,nombre,list_indices_prod):
    inicial=1
    for i in range(N):
        empty.acquire()
        try:
            nuevo=random.randint(inicial, 10*(i+1))
            storage[list_indices_prod[nombre]%NInd] = nuevo
            print (f"El productor {nombre} esta produciendo: {nuevo} en la \
                   posiscion {list_indices_prod[nombre]}\n")
            list_indices_prod[i]+=1
            index.value += 1
            inicial=nuevo
        finally:
            non_empty.release()
    empty.acquire()
    storage[i]=-2
    non_empty.release()

def minimo(lista):
    resultado=lista[0]
    for i in lista:
        if i[0]<resultado[0]:
            resultado = i
    return resultado

def get_data(storage, index, mutex):
    mutex.acquire()
    fin=0
    try:
        lista=[]
        #Recorro el storage que tiene el almacende los productores y usando la lista de indices que
        #tiene la posicion del elemento a consumir, los meto en una lista y elijo el minimo
        for i in range(NPROD):
            if index[i]<N:
                if storage[i][(index[i])%NInd]>=0:
                    lista.append((storage[i][index[i]],i))
        if lista!=[]:
            data=minimo(lista)
            index[data[1]] = index[data[1]]+1
        else:
            data=-1
            fin=1
    finally:
        mutex.release()
    return data,fin



def consumer(storage, mutex,list_ind,storage_final,empty,non_empty):
    for i in non_empty:
        i.acquire()
    fin=0
    while fin==0:
        dato,fin =get_data(storage, list_ind, mutex)
        if fin!=1:
            empty[dato[1]].release()
            storage_final.append(dato[0])
            print (f"El consumidor ha almacenando el valor {dato[0]} generado por \
el productor {dato[1]}\n")
            non_empty[dato[1]].acquire()
    print(storage_final)
        

def main():
    mutex = Lock()
    index = Value('i', 0)
    #Usaré una lista de inidices pq al tener un tamano fijo para el storage de cada productor
    #necesitare saber a que indice le corresponde introducir a cada productor, y tb
    #usare una lista de indices para saber a que 
    lista_indices_prod=[0]*NPROD #Pasamos a cada productor su indice
    lista_indic_consum=[0]*NPROD
    #NInd=3
    storage = [Array('i', NInd) for i in range(NPROD)]
    #Vaciamos el storage inicial
    for i in range(NPROD):
        for k in range(NInd):
            storage[i][k]=-2
    empty = [Semaphore(NInd) for i in range(NPROD)]
    non_empty= [Semaphore(0) for i in range(NPROD)]
    storage_final=[]
    prodlst = [Process(target=producer,
                       name=f'prod_{i}',
                       args=(storage[i],index,empty[i],non_empty[i],mutex,i,lista_indices_prod))
               for i in range(NPROD)]

    cons = Process(target=consumer,
                   name='cons',
                   args=(storage, mutex,lista_indic_consum,storage_final,empty,non_empty))

    for p in prodlst + [cons]:
        p.start()

    for p in prodlst + [cons]:
        p.join()

if __name__ == '__main__':
    main()