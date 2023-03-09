"""
@author: Daniel Martinez Martin
"""

from multiprocessing import Process, Lock, Semaphore, Value, Array
import random

#El numero de productores y numeros de elementos de cada productor puede ser modificado
NPROD = 10
N = 5# número de elementos que produce cada productor


def producer(storage, index, empty,non_empty, mutex,nombre):
    """
    Lo que varía respecto del archivo anterior Practica 1 es la incorporacion 
    del indice que se va sumando.
    """
    inicial=1
    for i in range(N):
        empty.acquire()
        try:
            nuevo=random.randint(inicial, 10*(i+1))
            storage[i] = nuevo
            print (f"El productor {nombre} esta produciendo: {nuevo}\n")
            index.value += 1
            inicial=nuevo
        finally:
            non_empty.release()
    empty.acquire()
    storage[i]=-1
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
                if storage[i][index[i]]>=0:
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
    #necesitare saber a que indice le corresponde introducir a cada productor
    lista_indices=[0]*NPROD
    
    storage = [Array('i', N) for i in range(NPROD)]
    empty = [Semaphore(1) for i in range(NPROD)]
    non_empty= [Semaphore(0) for i in range(NPROD)]
    storage_final=[]
    prodlst = [Process(target=producer,
                       name=f'prod_{i}',
                       args=(storage[i],index,empty[i],non_empty[i],mutex,i))
               for i in range(NPROD)]

    cons = Process(target=consumer,
                   name='cons',
                   args=(storage, mutex,lista_indices,storage_final,empty,non_empty))

    for p in prodlst + [cons]:
        p.start()

    for p in prodlst + [cons]:
        p.join()

if __name__ == '__main__':
    main()