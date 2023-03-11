"""
@author: Daniel Martinez Martin
"""

from multiprocessing import Process, Lock, Semaphore, Value, Array
import random

NPROD = 6
N = 5# número de elementos que produce cada productor
NInd=3 #numero de elemtnos que tendra el buffer limitado correspondiente a cada productor
       


def producer(storage, index, empty,non_empty,nombre,list_indices_prod,mutex_prod):
    """
    la función que funciona como un productor toma tres tipos distintos de semaforos,
    el empty y el  non-empty que ya estaban en la parte no opcional que señalan si 
    hay hueco o no y un mutex eclusivo a cada productor.
    El mutex se encarga de que solo pueda producir un elemento a la vez, ya que necesita
    marcar la siguiente posicion del buffer cuando pone un elemento. También se ha
    cambiado el seamforo empty a un Semaphore(NInd) para que señale que al principio
    tiene tantos huecos libres como la capacidad del buffer.
    Se usa el inicial=1 para generar los numeros crecientes, ya que cada vuelta de
    bucle aumenta el valor, la cantidad que aumente puede ser modificada.
    """
    inicial=1
    for i in range(N):
        mutex_prod.acquire()
        empty.acquire() 
        try:
            nuevo=random.randint(inicial, 10*(i+1))
            storage[list_indices_prod[nombre]%NInd] = nuevo
            print (f"El productor {nombre} esta produciendo: {nuevo} en la \
posiscion {list_indices_prod[nombre]%NInd}\n")
            list_indices_prod[nombre]+=1
            index.value += 1
            inicial=nuevo
        finally:
            non_empty.release()
            mutex_prod.release()
    empty.acquire()
    storage[0]=-1
    non_empty.release()

def minimo(lista):
    """
    Funcion que se usa para escoger el minimo valor a consumir, devolviendo
    el valor junto con el productor que lo habia producido.
    """
    resultado=lista[0]
    for i in lista:
        if i[0]<resultado[0]:
            resultado = i
    return resultado


def comprobar(storage):
    """
    Esta funcion sirve para comprobar si todos los productores han terminado
    sus producciones, para ello comprueba que todos hayan puesto el menos uno.
    """
    numMUno=0
    for i in range(NPROD):
        for k in storage[i]:
            if k==-1:
                numMUno+=1
    if numMUno==NPROD:
        return True
    else:
        return False
    
def get_data(storage, index, mutex):
    """
    Recorro el storage que tiene el almacen de los productores y usando la lista 
    de indices a consumir, se meten en una lista y se elije el minimo de ellos.
    El elegido señala al productor para al que se le avanza +1 en la lista de 
    indices a consumir.
    """
    mutex.acquire()
    fin=0
    try:
        lista=[]
       
        for i in range(NPROD):
            if index[i]<N:
                if storage[i][(index[i])%NInd]>=0:
                    lista.append((storage[i][index[i]],i))
        if lista!=[]:
            data=minimo(lista)
            index[data[1]] = index[data[1]]+1
        else:
            if comprobar(storage):
                data=-1
                fin=1
            else:
                fin=0
    finally:
        mutex.release()
    return data,fin


def consumer(storage, mutex,list_ind,storage_final,empty,non_empty):
    """
    Se hace uso de una variable auxiliar fin que nos indicara si se ha terminado
    la produccion. El fin se mantiene igual a 0 si todavia queda algun productor 
    produciendo y cuando es menos uno significa que la funcion comprobar anterior
    ha detectado que todos han terminado de producir.
    """
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
    mutex_sem = [Semaphore(1) for i in range(NPROD)]
    index = Value('i', 0)
    #Una lista de indices para los productores, que sepan donde les toca producir,
    # y otra para que el consumidor sepa cual tiene que consumir. Se inicia en 0.
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
                       args=(storage[i],index,empty[i],non_empty[i],i,lista_indices_prod,mutex_sem[i]))
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
