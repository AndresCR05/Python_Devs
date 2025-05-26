#Se importan las dependencias
import keyboard
import time
import pymsgbox


#Lista de posibles teclas
teclas = ['a', 's', 'd', 'f']

while True:
    #Se recorren las posibles teclas
    for tecla in teclas:
        #Si la tecla es presionada
        if keyboard.is_pressed(tecla):
            #Genera una alerta
            pymsgbox.alert(f"La tecla {tecla.upper()} fue presionada!", "Alerta de Tecla Presionada")
            #Espera 0.2 s
            time.sleep(0.2) 
    #Si presiona ESC, termina el programa        
    if keyboard.is_pressed('esc'):
        break