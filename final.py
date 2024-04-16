# -*- coding: utf-8 -*-

mensajehexadecimal = '209DF693E30700F0EB2F021854540400FF2510030A54667C'
mensajedecimal = int(mensajehexadecimal, 16)
mensajebinario = bin(mensajedecimal)[2:].zfill(8)

for i in range(1,4):
  if len(mensajebinario)%4 !=0:
    mensajebinario = "0"+mensajebinario

#end if
#Esto es necesario porque al pasar a bits eliminamos los bits que no son significativos al inicio
# Dividir la cadena de bits en sublistas de 8 elementos
listabytes = [mensajebinario[i:i+8] for i in range(0, len(mensajebinario), 8)]
bytesinv =  [''.join(byte[::-1]) for byte in listabytes] #invertir la lsta de bytes
# Convertir los bytes invertidos de vuelta a una cadena de bits
bitsinvertidos = ''.join([bin(int(byte, 2))[2:].zfill(8) for byte in bytesinv])
#1-ID del mensaje
IDmensaje = bitsinvertidos [0:6]
IDdecimal = int(IDmensaje,2)
print(f"El ID del mensaje es: {IDdecimal}")
if IDdecimal in [1, 2, 3]:

  #2-Indicador de repeticion
  rep = bitsinvertidos[6:8]
  repdecimal = int(rep,2)
  print(f"El mensaje se ha repetido: {repdecimal} veces")

  #3- ID del usuario, 30 bits siguientes:
  idusuario = bitsinvertidos [8:38]
  usuariodecimal = int(idusuario,2)
  print(f"El ID usuario es {usuariodecimal}")

  #4-Estado de navegación:
  status = bitsinvertidos[38:42]
  statusdecimal = int(status,2)
  print(f"El status es {statusdecimal}")

  #5-Velocidad de giro:
  vgiro = bitsinvertidos[42:50]
  vgirodecimal = int(vgiro,2)
  if vgirodecimal == 128:
    print(f"La velocidad de giro no está definida")
  else:
    print(f"La velocidad de giro es :{vgirodecimal}")

  #6-SOG
  sog = bitsinvertidos[50:60]
  sogdecimal = int(sog,2)
  print(f"La velocidad sobre tierra de paso es: {sogdecimal}")

  #7-Exactitud de la posición:
  exac = bitsinvertidos[60:61]
  if exac == 0:
    print(f"La exactitud es baja (>10m.)")
  else:
    print(f"La exactitud es alta (<10m.)")

  #8-Longitud en grados:
  longitud = bitsinvertidos[62:89]
  signo = bitsinvertidos[61:62]
  signodecimal =int(signo,2)
  if signodecimal == 1:#el numero es negativo, hay que hallar su CA2
    #Hallamos el CA2
    ca1 = ''.join('1' if bit == '0' else '0' for bit in longitud)

    ca2 =  bin(int(ca1, 2) + 1)
    ca2decimal = int(ca2,2)

    print(f"La longitud es: {-ca2decimal/600000}º")
  else:
      longituddecimal = int(longitud,2)
      print(f"La longitud es: {longituddecimal/600000}º")

  #9-LAtitud:
  latitud = bitsinvertidos[90:116]
  signolat = bitsinvertidos [89:90]
  signolatdecimal = int(signolat,2)
  if signolatdecimal ==1:
    ca1 = ''.join('1' if bit == '0' else '0' for bit in latitud)
    ca2 =  bin(int(ca1, 2) + 1)
    ca2decimal = int(ca2,2)
    print(f"La latitud es: {-ca2decimal/600000}º")
  else:
    latituddecimal = int(latitud,2)
    print(f"La latitud es: {latituddecimal/600000}º")

  #10-COG, rumbo sobre tierra:
  cog = bitsinvertidos[116:128]
  cogdecimal = int(cog,2)
  print(f"El rumbo sobre tierra es: {cogdecimal}")
  #11-Rumbo verdadero:
  rumbo = bitsinvertidos[128:137]
  rumbodecimal = int(rumbo,2)
  if rumbodecimal ==511:
      print(f"El rumbo verdadero no esta disponible")
  else:
      print(f"El rumbo verdadero es {rumbodecimal}º")
  #12-Tiempo
  tiempo = bitsinvertidos[137:143]
  tiempodecimal = int(tiempo,2)
  print(f"El tiempo es: {tiempodecimal}")
  #13-Maniobra
  maniobra = bitsinvertidos[143:145]
  maniobradec = int(maniobra,2)
  if maniobradec ==0:
     print(f"Maniobra especial no disponible")
  if maniobradec==1:
     print(f"No hay maniobra especial ")
  if maniobradec == 2:
     print(f"Hay maniobra especial ")

  #14-Reserva, son 3 bits que deberian estar a 0, es el caso
  reserva = bitsinvertidos[145:148]
  reservadec = int(reserva,2)
  #15-RAIM: supervisión de integridad autónoma de receptor
  raim = bitsinvertidos [148:149]
  raimdec = int(raim,2)
  print(f"Bandera RAIM {raimdec}")
  #16- Estado de sincronización_
  sinc = bitsinvertidos[149:151]
  sincdecimal = int(sinc,2)
  print(f"El estado de sincronización es: {sincdecimal}")
  #17-Temporizacion , Especifica las tramas que quedan hasta una nueva selección de intervalo de tiempo
  temp = bitsinvertidos [149:152]
  tempdecimal = int(temp,2)
  if tempdecimal ==0:
    print(f"La última transmisión fue en este intervalo")
  else:
    print(f"Quedan {tempdecimal} tramas hasta el cambio de intervalo")
  #18-Submensaje
  sub = bitsinvertidos [152:166]
  subdecimal = int(sub,2)
  print(f"El submensaje es: {subdecimal}")
