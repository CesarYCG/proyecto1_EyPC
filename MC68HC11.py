from LeerArchivos import *
from string import hexdigits
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import *

    ##=====================================================##
    ##===============CLASES DEL PROGRAMA===================##
    


###El fist_espace es el que determina como leer el archivo, es decir que lineas tomar o no para el analisis, las que 
#no tienen espacio al principio no las lee ya que solo son nombres de etiquetas, constantes o comentario, variables, etc.
class Program(object):
    #define variable a usar, metodos
    def __init__(self,name):
        
        self.name = name
        self.comienzo = False
        self.final = False
        self.start_memory = '0'
        self.memory_posicion = 0
        self.memoria = []
        self.org_memoria = []
        self.bullet = self.start_memory
        self.num_bullet = 0
        self.var = {}
        self.linea_posicion = 0
        self.etiqueta = {}
        self.cod_objeto = {}
        self.total_lineas = 0
        self.errores = 0
        self.num_codigo = 0
        self.salto_etiqueta = {}

class Errores(BaseException):                                   #Calculando cuantos errores hay en el programa
    def __init__(self,codigo,error_linea,op_name = ''):
        self.error_linea = str(error_linea)                     #La palabra que este mal se guardará en un a cadena
        self.op_name = op_name
        self.codigo = codigo
        programa.errores +=1



        ##======================================================================================##
        ##=========================FUNCIONES PARTICULARES DEL===================================##
        ##=========================LOS MNEMONICOS y DIRECTIVAS==================================##
        ##================================DEL MC68HC11==========================================##
        ##======================================================================================##


def BNE(valor,tag,op_name):
    
    if valor == "no_valor":
        valor = tag
    if valor in programa.etiqueta:
        programa.memoria.append(valuesREL[op_name]+salto_Relativo(programa.etiqueta[tag],programa.memory_posicion))
    elif valor in programa.salto_etiqueta:
        programa.salto_etiqueta.update({valor:[valuesREL[op_name],programa.total_lineas,programa.salto_etiqueta[valor][2]+1,programa.memory_posicion+2]})
        programa.memoria.append(valor)
    else:
        programa.salto_etiqueta.update({valor:[valuesREL[op_name],programa.total_lineas,1,programa.memory_posicion]})
        programa.memoria.append(valor)
    programa.memory_posicion+=2
    if tag != "sin_etiqueta" and tag not in programa.etiqueta:
        programa.etiqueta.update({tag:programa.memory_posicion})
        
def BRCLR(valor,tag,op_name):
    
    mnem_extra = 0
    if 'X' in valor or 'Y' in valor:
        if 'X' in valor:
            valor = particular[op_name][1]+clr_valor(valor)
        else:
            valor = particular[op_name][2]+clr_valor(valor)
    else:
        valor = particular[op_name][0]+clr_valor(valor)
    programa.memoria.append(valor)                               #agregamos el valor de BRCLR a la lista 
    programa.memory_posicion += int(len(programa.memoria[-1])/2)
    if tag in programa.etiqueta:
        programa.memoria[-1]=programa.memoria[-1]+salto_Relativo(programa.etiqueta[tag],programa.memory_posicion-1)
        mnem_extra += 1
    elif tag in programa.salto_etiqueta:
        programa.salto_etiqueta.update({tag:[valor,programa.total_lineas,programa.salto_etiqueta[valor][2]+1,programa.memory_posicion,op_name]})
        programa.memoria[-1] = tag
        mnem_extra += 1
    elif tag != "sin_etiqueta":
        programa.salto_etiqueta.update({tag:[valor,programa.total_lineas,1,programa.memory_posicion,op_name]})
        programa.memoria[-1] = tag
    programa.memory_posicion += mnem_extra

def EQU(valor,name,op_name):
    
    if int(valor.replace('$',''),16)<=int('FF',16):
        valor = valor[3:]
    programa.var.update({name:valor.replace('$','')})             #agregamos el valor a nombre en el diccionario
    programa.memoria.append(valor.replace('$',''))                #con append se agrega el valor a la lista

def END(valor,tag,op_name):
    
    programa.final = True
    programa.cod_objeto.update({programa.total_lineas:op_name.ljust(8)+(valor if valor != 'no_valor' else '')})

def FCB(valor1):
    
    programa.memoria.append(clr_valor(valor1)+' ')

def JMP(valor,tag,op_name):
    
    if valor == "no_valor":
        valor = tag
    if valor in programa.salto_etiqueta:
        programa.salto_etiqueta.update({valor:[valuesEXT[op_name],programa.total_lineas,programa.salto_etiqueta[valor][2]+1]})
        programa.memoria.append(valor)
        programa.memory_posicion += 3
    elif valor in programa.etiqueta:
        programa.memoria.append(valuesEXT[op_name]+hex(programa.etiqueta[tag]).upper()[2::])
        programa.memory_posicion += 3
    elif clr_valor(valor).isnumeric() or clr_valor(valor) in programa.var:
        if (len(clr_valor(valor)) != 2 or len(clr_valor(valor)) != 4) and clr_valor(valor) not in programa.var:
            raise Errores(1,programa.total_lineas)
        if ',X' in valor:
            programa.memoria.append(indiceadox[op_name]+clr_valor(valor))
            programa.memory_posicion += 2
        elif ',Y' in valor:
            programa.memoria.append(indiceadoy[op_name]+clr_valor(valor))
            programa.memory_posicion += 3
        elif len(clr_valor(valor)) == 2:
            programa.memoria.append(valuesDIR[op_name]+clr_valor(valor))
            programa.memory_posicion += 2
        else:
            valor = programa.var[valor]
            while len(valor) < 4:
                valor = '0'+valor
            programa.memoria.append(valuesEXT[op_name]+valor)
            programa.memory_posicion += 3
    else:
        programa.salto_etiqueta.update({valor:[valuesEXT[op_name],programa.total_lineas,1]})
        programa.memoria.append(valor)
        programa.memory_posicion += 3

def NOP(valor, tag,op_name):
    
    if valor != "no_valor":
        raise Errores(8,programa.total_lineas)
    programa.memoria.append(valuesINH[op_name])
    verifica_etiqueta(tag)   
    
    
        ##=====================================================##
        ##===============FUNCIONES DEL PROGRAMA================##
        ##=====================================================##

def INICIO(inicia_memoria_org,tag,op_name):                          # valor que toma ORG en memoria
    if not programa.comienzo:
        programa.start_memory = clr_valor(inicia_memoria_org)      #inicio programa Memoria en base hexadecimal
        programa.memory_posicion = int(programa.start_memory,16) #Nos devuelve al valor del inicio del programa en entero
        programa.comienzo = True
    verifica_longitud(programa.start_memory, 2)
    auxiliar = int(clr_valor(inicia_memoria_org), 16)
    programa.org_memoria.append(hex(auxiliar).upper()[2::])
    programa.memoria.append(hex(auxiliar).upper()[2::])
    
def set_bullet(item):
    memoria = int(programa.bullet, 16)          #Memoria en base hexadecimal 
    if item == 8:
        temp_aux = 4
    elif item == 6:
        temp_aux = 3
    elif item == 4:
        temp_aux = 2
    else:
        temp_aux = 1
    memoria += int(temp_aux)
    programa.bullet = hex(memoria)[2::].upper()

def clr_valor(valor):                                        #quita caracteres que no se deben mostrar en el lst
    valor = valor.replace('#','')                                #.replace() sustituye la variable encontrada por nada
    valor = valor.replace('$','')
    valor = valor.replace(',X','')
    valor = valor.replace(',Y','')
    valor = valor.replace(',','')
    if valor not in programa.var and valor not in programa.etiqueta and valor not in programa.salto_etiqueta:
        valor_hex = True
        for letter in valor:
            if letter not in hexdigits:
                valor_hex = False

        if valor_hex:
            if len(valor)==3 or len(valor)==1:                  # para palabras de 4 bytes
                while len(valor)!=4:
                    valor = '0'+valor
    return valor

def verifica_longitud(valor,byts):                                    #lanza el error si el operando es erroneo, no hay congruencia en etiquetas y/o constantes
    if len(valor) != byts*2:
        raise Errores(1,programa.total_lineas)
    elif not valor.isnumeric() and (valor not in programa.etiqueta or valor not in programa.var):
        raise Errores(6 if valor not in programa.var else 4,programa.total_lineas)


def verifica_etiqueta(tag):                                         #verifica etiquetas
    if tag != "sin_etiqueta" and tag not in programa.etiqueta:
        programa.etiqueta.update({tag:programa.memory_posicion})    #agrega el valor de la etiqueta
    programa.memory_posicion += int(len(programa.memoria[-1])/2)

def salto_Relativo(X,Y):                                        #hace saltos valuesRELs
    salto_R = X - Y - 2
    if abs(salto_R)>127:
        raise Errores(2,programa.total_lineas)
    if salto_R<0:
        salto_R = int(bin(salto_R)[3::],2) - (1 << 8)
    salto_R = hex(salto_R)[3 if salto_R < 0 else 2::].upper()
    while len(salto_R)<2:
        salto_R = '0'+salto_R
    return salto_R


def ajuste_De_Linea(lista,first_space):                              #aquí se ajustan los colores de la impresión
    if len(lista)==3 and first_space:                            
        f_linea = ''.ljust(9)+lista[0].ljust(8)+lista[1].ljust(15)+lista[2]
    elif len(lista) == 3:
        f_linea = lista[0].ljust(9)+lista[1].ljust(8)+lista[2]
    elif len(lista) == 2 and first_space:
        f_linea = ''.ljust(9)+lista[0].ljust(8)+lista[1]
    elif len(lista) == 2:
        f_linea = lista[0].ljust(9)+lista[1]
    elif first_space:
        f_linea = ''.ljust(9)+lista[0]
    else:
        f_linea = lista[0]
    return f_linea
##Esta función regresa la linea sin los comentarios
def quita_comentarios(linea):
    linea = linea.split()                                       #split separa las palabras que encuentra en una linea
    for item in linea:
        if '*' in item:
            for x in range(len(linea)-1,linea.index(item)-1,-1): #recorre la linea en un intervalo de inicio hasta el comentario
                linea.pop(x)                                     #pop() Devuelve el ultimo valor de la linea
    return linea                                               




        ##======================================================================================##
        ##==============================FUNCIONES PARA LOS =====================================##
        ##===========================MODOS DE DIRECCIONAMIENTO==================================##
        ##================================DEL MC68HC11==========================================##
        ##======================================================================================##

def LDX(valor,tag,op_name):                                       
    if clr_valor(valor) in programa.var:                      
        if '#' in valor:
            programa.memoria.append(valuesIMM[op_name]+programa.var[clr_valor(valor)]) #Se manda 
        elif len(programa.var[clr_valor(valor)])==2 and op_name in valuesDIR:                  
            programa.memoria.append(valuesDIR[op_name]+programa.var[clr_valor(valor)])
        elif len(programa.var[clr_valor(valor)])==4:
            programa.memoria.append(valuesEXT[op_name]+programa.var[clr_valor(valor)])
        else:
            programa.memoria.append(valuesEXT[op_name]+programa.var[clr_valor(valor)]) #OPTIMIZACIÓN DE CÓDIGO
    elif '#' in valor:                                            #valuesIMM
        valor = clr_valor(valor)
        if '\'' in valor:
            programa.memoria.append(valuesIMM[op_name]+hex(ord(valor.replace('\'','')))[2::].upper())
        elif len(valor) == 2 or len(valor) == 4:
            programa.memoria.append(valuesIMM[op_name]+valor)
        else:
            raise Errores(1,programa.total_lineas)
    elif ',' in valor:                                            #INDEXADO
        if 'X' in valor:#X
            valor = clr_valor(valor)
            verifica_longitud(valor, 1)
            programa.memoria.append(valuesINDX[op_name]+valor)
        elif 'Y' in valor:#Y
            valor = clr_valor(valor)
            verifica_longitud(valor, 1)
            programa.memoria.append(valuesINDY[op_name]+valor)
        else:
            raise Errores(7,programa.total_lineas)
    elif '$' in valor:                                            #DIRECTO O EXTENDIDO
        valor = clr_valor(valor)
        if len(valor) == 2:
            programa.memoria.append(valuesDIR[op_name]+valor.replace('$',''))
        elif len(valor) == 4:
            programa.memoria.append(valuesEXT[op_name]+valor.replace('$',''))
        else:
            raise Errores(1,programa.total_lineas)
    elif valor == "no_valor":
        raise Errores(7,programa.total_lineas)
       
    verifica_etiqueta(tag)                                           

        ##=====================================================================================##
        ##========================MNEMONICOS PARA LAS FUNCIONES================================##
        ##==========================PARTICULARES DEL MC68HC11==================================##
        ##=====================================================================================##
mnemonico = {
'ABA':NOP,'ABX':NOP,'ABY':NOP, 'ADCA':LDX,'ADCB':LDX,'ADDA':LDX,'ADDB':LDX,'ADDD':LDX,'ANDA':LDX,
'ANDB':LDX,'ASL':LDX,'ASLA':NOP, 'ASLB':NOP,'ASLD':NOP,'ASR':LDX,'ASRA':NOP,'ASRB':NOP,'BCC':BNE,
'BCLR':BRCLR, 'BCS':BNE, 'BEQ':BNE,'BGE':BNE,'BGT':BNE,'BHI':BNE,'BHS':BNE,'BITA':LDX,'BITB':LDX,
'BLE':BNE,'BLO':BNE, 'BLS':BNE, 'BLT':BNE, 'BMI':BNE,'BNE':BNE,'BPL':BNE,'BRA':BNE,'BRCLR':BRCLR,
'BRN':BNE,'BRSET':BRCLR,'BSET':BRCLR,'BSR':BNE,'BVC':BNE,'BVS':BNE,'CBA':NOP,'CLC':NOP,'CLI':NOP,
'CLR':LDX,'CLRA':NOP,'CLRB':NOP,'CLV':NOP, 'CMPA':LDX,'CMPB':LDX,'COM':LDX,'COMA':NOP,'COMB':NOP,
'CPD':LDX,'CPX':LDX,'CPY':LDX,'DAA':NOP, 'DEC':LDX, 'DECA':NOP, 'DECB':NOP, 'DES':NOP, 'DEX':NOP,
'DEY':NOP,'END':END,'EORA':LDX,'EORB':LDX,'EQU':EQU,'FCB':FCB, 'FDIV':NOP, 'IDIV':NOP, 'INC':LDX,
'INCA':NOP,'INCB':NOP,'INS':NOP,'INX':NOP, 'INY':NOP, 'JMP':JMP, 'JSR':JMP,'LDAA':LDX,'LDAB':LDX,
'LDD':LDX, 'LDS':LDX, 'LDX':LDX, 'LDY':LDX, 'LSL':LDX,'LSLA':NOP,'LSLB':NOP,'LSLD':NOP,'LSR':LDX,
'LSRA':NOP, 'LSRB':NOP,'LSRD':NOP,'MUL':NOP,'NEG':LDX,'NEGA':NOP,'NEGB':LDX,'NOP':NOP,'ORAA':LDX,
'ORAB':LDX, 'ORG':INICIO, 'PSHA':NOP, 'PSHB':NOP, 'PSHX':NOP, 'PSHY':NOP, 'PULA':NOP, 'PULB':NOP,
'PULX':NOP, 'PULY':NOP,'ROL':LDX,'ROLA':NOP,'ROLB':NOP,'ROR':LDX,'RORA':NOP,'RORB':NOP,'RTI':NOP,
'RTS':NOP,'SBA':NOP, 'SBCA':LDX, 'SBCB':LDX, 'SEC':NOP,'SEI':NOP,'SEV':NOP,'STAA':LDX,'STAB':LDX,
'STD':LDX,'STOP':NOP,'STS':LDX,'STX':LDX, 'STY':LDX, 'SUBA':LDX, 'SUBB':LDX,'SUBD':LDX,'SWI':NOP,
'TAB':NOP, 'TAP':NOP,'TBA':NOP,'TETS':NOP,'TPA':NOP,'TST':LDX, 'TSTA':NOP, 'TSTB':NOP, 'TSX':NOP,
'TSY':NOP,'TXS':NOP,'TYS':NOP,'WAI':NOP,'XGDX':NOP,'XGDY':NOP,
'aba':NOP,'abx':NOP,'aby':NOP, 'adca':LDX,'adcb':LDX,'adda':LDX,'addb':LDX,'addd':LDX,'anda':LDX,
'andb':LDX,'asl':LDX,'asla':NOP, 'aslb':NOP,'asld':NOP,'asr':LDX,'asra':NOP,'asrb':NOP,'bcc':BNE,
'bclr':BRCLR, 'bcs':BNE, 'beq':BNE,'bge':BNE,'bgt':BNE,'bhi':BNE,'bhs':BNE,'bita':LDX,'bitb':LDX,
'ble':BNE,'blo':BNE, 'bls':BNE, 'blt':BNE, 'bmi':BNE,'bne':BNE,'bpl':BNE,'bra':BNE,'BRCLR':BRCLR,
'brn':BNE,'brset':BRCLR,'bset':BRCLR,'bsr':BNE,'bvc':BNE,'bvs':BNE,'cba':NOP,'clc':NOP,'cli':NOP,
'clr':LDX,'clra':NOP,'clrb':NOP,'clv':NOP, 'cmpa':LDX,'cmpb':LDX,'com':LDX,'coma':NOP,'comb':NOP,
'cpd':LDX,'cpx':LDX,'cpy':LDX,'daa':NOP, 'dec':LDX, 'deca':NOP, 'decb':NOP, 'des':NOP, 'dex':NOP,
'dey':NOP,'end':END,'eora':LDX,'eorb':LDX,'equ':EQU,'fcb':FCB, 'fdiv':NOP, 'idiv':NOP, 'inc':LDX,
'inca':NOP,'incb':NOP,'ins':NOP,'inx':NOP, 'iny':NOP, 'jmp':JMP, 'jsr':JMP,'ldaa':LDX,'ldab':LDX,
'ldd':LDX, 'lds':LDX, 'LDX':LDX, 'ldy':LDX, 'lsl':LDX,'lsla':NOP,'lslb':NOP,'lsld':NOP,'lsr':LDX,
'lsra':NOP, 'lsrb':NOP,'lsrd':NOP,'mul':NOP,'neg':LDX,'nega':NOP,'negb':LDX,'NOP':NOP,'oraa':LDX,
'orab':LDX, 'org':INICIO, 'psha':NOP, 'pshb':NOP, 'pshx':NOP, 'pshy':NOP, 'pula':NOP, 'pulb':NOP,
'pulx':NOP, 'puly':NOP,'rol':LDX,'rola':NOP,'rolb':NOP,'ror':LDX,'rora':NOP,'rorb':NOP,'rti':NOP,
'rts':NOP,'sba':NOP, 'sbca':LDX, 'sbcb':LDX, 'sec':NOP,'sei':NOP,'sev':NOP,'staa':LDX,'stab':LDX,
'std':LDX,'stop':NOP,'sts':LDX,'stx':LDX, 'sty':LDX, 'suba':LDX, 'subb':LDX,'subd':LDX,'swi':NOP,
'tab':NOP, 'tap':NOP,'tba':NOP,'tets':NOP,'tpa':NOP,'tst':LDX, 'tsta':NOP, 'tstb':NOP, 'tsx':NOP,
'tsy':NOP,'txs':NOP,'tys':NOP,'wai':NOP,'xgdx':NOP,'xgdy':NOP
}



        ##=====================================================##
        ##===============FUNCIONES DEL PROGRAMA================##
        ##=====================================================##

#Ventana
window=Tk()
window.title("MC68HC11")
window.geometry('400x230')
window.configure(background='gray77')
#Contenido
welcome=Label(window,text="        BIENVENIDO          ",font=("Arial Bold", 20),background='gray77').place(x=90,y=5)
welcome=Label(window,text="    AL COMPILADOR     ",font=("Arial Bold", 20),background='gray77').place(x=90,y=45)
Etiqueta1= Label(window,text="1.-Ingrese el nombre del archivo con extensión *.ASC",font=("Agency FB",10),background='gray77').place(x=5,y=100)
Etiqueta2=Label(window,text="2.-Presione el boton Complilar",font=("Agency FB",10),background='gray77').place(x=5,y=130)
imagen=PhotoImage(file="MC68HC11_logo.png")
fondo=Label(window,image=imagen).place(x=0,y=0)
entrada=StringVar()
txt = Entry(window,width=30,textvariable=entrada)
txt.place(x=170,y=174)
def clicked():
    if (entrada.get()).endswith(".ASC"):
        messagebox.showinfo('Exito','Cierre el programa para continuar')
        return entrada.get()
    else:
        messagebox.showinfo('Error','Archivo no valido\nDebe ser de tipo *.ASC')
btn = Button(window,text='Complilar', command=clicked, width=15)
btn.place(x=40,y=170)
window.mainloop() #Todo lo de arriba se va a ejecutar hasta que se cierre 
programa = 1
programa=Program(clicked())

try:
    file = open(programa.name,"r")
    f = open(programa.name.replace('.ASC','.lst'), "w")
    h = open(programa.name.replace('.ASC','.hex'), "w")
except:  
    messagebox.showinfo('Error','ERROR 404 ARCHIVO NOT FOUND\nNO SE ENCONTRO EL ARCHIVO, ¡HASTA LUEGO!')
    exit(-1)
        
#--lee linea por linea 
for linea in file:
    first_space = True if linea[0] == ' ' or linea[0] == '\t' else False  ##Solo va a analizar las lineas que tengan un espacio o tabulación al principio
    linea = quita_comentarios(linea)

  
    programa.total_lineas+=1
    
    
    if len(linea)>0:
        programa.linea_posicion+=1                                                              #ajuste de linea
        programa.cod_objeto.update({programa.linea_posicion:ajuste_De_Linea(linea,first_space)})  
      
    try:
        if len(linea)>=2:
            if linea[0] in particular or linea[1] in particular:
                if linea[0] in mnemonico:
                    mnemonico[linea[0]](linea[1],linea[2] if len(linea) == 3 else "sin_etiqueta",linea[0])
                else:
                    raise Errores(3,programa.total_lineas,linea[0] if linea[0] in particular else linea[1])
                linea = ''
          

        if len(linea) == 3:
            if linea[1] not in mnemonico:
                raise Errores(3,programa.total_lineas,linea[1])
         
            if linea[1] == 'FCB':
                mnemonico[linea[1]](linea[2])
            elif linea[1] == 'fcb':
                mnemonico[linea[1]](linea[2])
            else:
                mnemonico[linea[1]](linea[2], linea[0],linea[1])
        elif len(linea) == 2:
            if linea[0] in mnemonico:
                if linea[1] in programa.etiqueta:
                    mnemonico[linea[0]]("no_valor", linea[1],linea[0])
                elif linea[0] == 'FCB':
                    mnemonico[linea[0]](linea[1])
                elif linea[0] == 'fcb':
                    mnemonico[linea[0]](linea[1])
                else:
                    mnemonico[linea[0]](linea[1], "sin_etiqueta",linea[0])
            elif linea[1] in mnemonico:
                mnemonico[linea[1]]("no_valor", linea[0],linea[1])
            else:
                raise Errores(3,programa.total_lineas,linea[0])
        elif len(linea) == 1:
            if linea[0] in mnemonico and first_space:
                mnemonico[linea[0]]("no_valor", "sin_etiqueta",linea[0])
            elif not first_space:
                programa.etiqueta.update({linea[0]:programa.memory_posicion})
            else:
                raise Errores(3,programa.total_lineas,linea[0])
    #errores
    except KeyError:
        print("ERROR 007 MAGNITUD DE OPERANDO ERRONEA"+str(programa.total_lineas)+' K')
    except Errores as e:
        if e.codigo == 1:
            print("ERROR 007 MAGNITUD DE OPERANDO ERRONEA "+e.error_linea)
        elif e.codigo == 2:
            print("ERROR 008 SALTO RELATIVO MUY LEJANO"+e.error_linea)
        elif e.codigo == 3:
            print("ERROR 004 MNEMÓNICO"+e.op_name+"\tINEXISTENTE EN LINEA"+e.error_linea)
        elif e.codigo == 4:
            print("ERROR 003 ETIQUETA "+e.op_name+"\tINEXISTENTE EN LINEA"+e.error_linea)
        elif e.codigo == 5:
            print("ERROR 002 VARIABLE "+e.op_name+"INEXISTENTE "+e.error_linea)
        elif e.codigo == 6:
            print("ERROR 001 CONSTANTE"+e.op_name+"INEXISTENTE EN LINEA "+e.error_linea)
        elif e.codigo == 7:
            print("ERROR 005 INSTRUCCIÓN CARECE DE OPERANDO(S)"+e.error_linea)
        elif e.codigo == 8:
            print("ERROR 006 INSTRUCCIÓN NO LLEVA OPERANDO(S)"+e.error_linea)
  
    #etiquetas salto relativo
for indice,entry in enumerate(programa.memoria):
    if entry in programa.salto_etiqueta and entry in programa.etiqueta:
        if programa.salto_etiqueta[entry][0] in valuesREL.values() or len(programa.salto_etiqueta[entry]) == 5:
            try:
                programa.memoria[indice]= str(programa.salto_etiqueta[entry][0])+salto_Relativo(programa.etiqueta[entry],programa.salto_etiqueta[entry][3])
            except Errores as e:
                print("ERROR 008 SALTO RELATIVO MUY LEJANO"+str(programa.salto_etiqueta[entry][1]))
        else:
            programa.memoria[indice]= str(programa.salto_etiqueta[entry][0])+hex(programa.etiqueta[entry])[2::].upper()
        programa.salto_etiqueta[entry][2]+=-1
for key in programa.salto_etiqueta:
    if programa.salto_etiqueta[key][2]>0:
        print("ERROR 003 ETIQUETA"+key+"\tINEXISTENTE EN LINEA"+str(programa.salto_etiqueta[key][1]))
        programa.errores += 1
        if programa.memoria.count(key)>1:
            print("\tETIQUETA INEXISTENTE PRESENTE"+str(programa.memoria.count(key))+" veces")
#error 9
if not programa.final:
    programa.errores += 1
    print("ERROR 010 NO SE ENCUENTRA END")
    
print('\n')
print('\n\t ====================RESULTADO======================')
print('\n\t Total de lineas: '+str(programa.total_lineas)+'\n\n\t Numero de errores: '+str(programa.errores))
if programa.errores > 0:
    exit(1)

'''Se compiló el programa en número de línea y el codigo objeto'''
pass_var = False
aumentar_espacios=1


try:
    for indice,item in enumerate(programa.memoria):
        indice+=aumentar_espacios
        if item in programa.org_memoria:               #obtenemos una lista de tuplas con método item
        ###Aquí se da el formato al archivo lst
            f.write(str(indice).ljust(4)+':'.ljust(8)+item.ljust(12)+':'+programa.cod_objeto[indice]+'\n')
            programa.bullet = item
        else:
            if item in programa.var.values() and programa.bullet == '0':
                f.write(str(indice).ljust(4)+':'.ljust(8)+item.zfill(4)+':'.rjust(9)+programa.cod_objeto[indice]+'\n')
            elif (programa.cod_objeto[indice][0]!=' ' and programa.cod_objeto[indice][0]!='\t') and len(quita_comentarios(programa.cod_objeto[indice])) == 1:
                while (programa.cod_objeto[indice][0]!=' ' and programa.cod_objeto[indice][0]!='\t') and len(quita_comentarios(programa.cod_objeto[indice])) == 1:
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+''.ljust(12)+':'+programa.cod_objeto[indice]+'\n')  #ETIQUETAS
                    indice+=1
                    aumentar_espacios+=1
                if(len(item)==2):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(9)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==4):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(7)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==8):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(3)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))

                else:
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(5)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
            else:
                if(len(item)==2):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(9)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==4):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(7)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
                elif(len(item)==8):
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(3)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
                else:
                    f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+'('+item+')'.ljust(5)+':'+programa.cod_objeto[indice]+'\n')
                    set_bullet(len(item))
    indice+=1
    while indice< len(programa.cod_objeto) and 'END' not in quita_comentarios(programa.cod_objeto[indice-1]):
        if programa.cod_objeto[indice][0]!=' ' and programa.cod_objeto[indice][0]!='\t':
          f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+item.ljust(12)+':'+programa.cod_objeto[indice]+'\n')
        else:
            f.write(str(indice).ljust(4)+':'+programa.bullet.ljust(7)+''.ljust(12)+':'+programa.cod_objeto[indice]+'\n')
        indice+=1
#dice el error y en la linea de codigo
except KeyError:
    print('Keyerror in linea'+str(indice)+item+programa.cod_objeto[indice-1])
#para tabla de simbolos
symbol_table = programa.etiqueta.copy()
symbol_table.update(programa.var)
symbol_table.update(programa.salto_etiqueta)
f.write('\nTabla de Simbolos, total: '+str(len(symbol_table))+'\n')
for key in sorted(symbol_table):
    if key in programa.etiqueta:
        f.write(key+'\t'+hex(programa.etiqueta[key])[2:].upper()+'\n')
    elif key in programa.salto_etiqueta:
        f.write(key+'\t'+hex(programa.salto_etiqueta[key])[2:].upper()+'\n')
    else:
        f.write(key+'\t'+('' if len(programa.var[key])==4 else '00' )+programa.var[key]+'\n')

bullet = 0
posicion = 1
#Para darle formato al archivo .hex
for item in programa.memoria:
    if item in programa.org_memoria:
        posicion = 1
        bullet = item
        h.write(('\n' if bullet != programa.org_memoria[0] else '<')+bullet+'> ')
    elif bullet != 0:
        while posicion<=16 and item != '':
            h.write(item[:2]+' ')
            item = item.replace(item[:2],'')
            posicion += 1
        if posicion > 16:
            posicion = 1
            bullet = str(hex(int(bullet,16)+16)[2:].upper()) #uppSer retorna la cadena en mayusculas en este caso el hexa
            h.write('\n<'+bullet+'> ')
            while item != '':
                h.write(item[:2]+' ')
                item = item.replace(item[:2],'')
                posicion += 1


#cierra flujos 
f.close()
h.close()
file.close()

#--Genera el archivo .lst 
#--Genera el archivo .hex 
print('\n\t Archivo lst ' +programa.name.replace('.ASC','.lst')+' creado correctamente')  
print('\n\t Archivo hex ' +programa.name.replace('.ASC','.hex')+' creado correctamente')  
print('\n\t ==================================================')
print('\n')