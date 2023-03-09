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
    Usaremos el inicial para ir generando numeros cada vez mas grande, el rango
    en el que crecen se puede modificar abajo con nuevo. Generemaos un numero y vemos
    con un semaforo que su posicion esta vacia, y al introducirlo notificamos con
    otro semaforo que la posicion esta llena.
    """
    inicial=1
    for i in range(N):
        empty.acquire()
        try:
            nuevo=random.randint(inicial, 10*(i+1))
            storage[nombre] = nuevo
            print (f"El productor {nombre} esta produciendo: {nuevo}\n")
            
            inicial=nuevo
        finally:
            non_empty.release()
    empty.acquire()
    storage[nombre]=-1
    non_empty.release()

def minimo(lista):
    """
    Funcion que nos permite devolver el productor que ha producido el menor numero
    en el storage compartido,junto con el propio elemento
    """
    resultado=lista[0]
    for i in lista:
        if i[0]<resultado[0]:
            resultado = i
    return resultado

def get_data(storage, mutex):
    """
    Funcion que devuelve el productor y elemento haciendo uso del semaforo mutex
    para garantizar que solo se extraiga un solo elemento cada vez
    """
    mutex.acquire()
    fin=0
    try:
        lista=[]
        for i in range(NPROD):
            if storage[i]>=0:
                lista.append((storage[i],i))
        if lista!=[]:
            data=minimo(lista)
        else:
            data=-1 #Este valor nunca se usara como tal solo sirve
                    #para devolver un entero cualquiera
            fin=1
    finally:
        mutex.release()
    return data,fin



def consumer(storage, mutex,storage_final,empty,non_empty):
    """
    Introduce el valor minimo obtenido en la lista final informando al semaforo
    del productor cuyo elemento ha consumido que su posicion esta vacia con su
    semaforo nonempty.
    """
    for i in non_empty:
        i.acquire()
    fin=0
    while fin==0:
        dato,fin =get_data(storage, mutex)
        if fin!=1:
            empty[dato[1]].release()
            storage[dato[1]]=-2
            storage_final.append(dato[0])
            print (f"El consumidor ha almacenando el valor {dato[0]} generado por \
el productor {dato[1]}\n")
            non_empty[dato[1]].acquire()
    print(storage_final)
        

def main():
    mutex = Lock()
    index = Value('i', 0)
    
    #El array tiene que ser un storage a cada uno le pone un valor un productor
    storage = Array('i', NPROD)
    for i in range(NPROD):
        storage[i]=-2
    empty = [Semaphore(1) for i in range(NPROD)]
    non_empty= [Semaphore(0) for i in range(NPROD)]
    storage_final=[]
    
    prodlst = [Process(target=producer,
                       name=f'prod_{i}',
                       args=(storage,index,empty[i],non_empty[i],mutex,i))
               for i in range(NPROD)]

    cons = Process(target=consumer,
                   name='cons',
                   args=(storage, mutex,storage_final,empty,non_empty))

    for p in prodlst + [cons]:
        p.start()

    for p in prodlst + [cons]:
        p.join()

if __name__ == '__main__':
    main()