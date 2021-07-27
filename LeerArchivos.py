import pandas as pd
# Obteniendo los valores desde el Excel INSTRUCCIONES

#Leyendo el contenido del excel
archivo_excel = pd.read_excel('INSTRUCCIONES.xls')
#print(archivo_excel.columns)

#Guardando la COLUMNA MNEMONICOS
mnemonico_excel = archivo_excel['MNEMONICO'].values

# Obteniendo los valores de los OPCODES
IMM= archivo_excel['OPCODE1'].values
DIR= archivo_excel['OPCODE2'].values
INDX= archivo_excel['OPCODE3'].values
INDY= archivo_excel['OPCODE4'].values
EXT= archivo_excel['OPCODE5'].values
INH= archivo_excel['OPCODE6'].values
REL= archivo_excel['OPCODE7'].values
#print(IMM)
# Diccionarios para guardar mnemonicos segun su clasificacion
dict_IMM={}
dict_DIR={}
dict_INDX={}
dict_INDY={}
dict_EXT={}
dict_INH={}
dict_REL={}
# Guardando los valores distintos a 'x' en las listas
# Esto se realiza comparando el valor de la columna en
# OPCODE y su correspondiente en la columna MNEMONICO
# del Excel. 
# Si el OPCODE es distinto de 'x', entonces al MNEMO
# correspondiente se le asignará el valor de la casilla
# ie: OPCODE1 de IMM, tiene el MNEMO 'adca' con valor 89
i=0
for mnemo in mnemonico_excel:
      if IMM[i]!='x':
            dict_IMM.update({mnemo:str(IMM[i])})
      if DIR[i]!='x':
            dict_DIR.update({mnemo:str(DIR[i])})
      if INDX[i]!='x':
            dict_INDX.update({mnemo:str(INDX[i])})
      if INDY[i]!='x':
            dict_INDY.update({mnemo:str(INDY[i])})
      if EXT[i]!='x':
            dict_EXT.update({mnemo:str(EXT[i])})
      if INH[i]!='x':
            dict_INH.update({mnemo:str(INH[i])})
      if REL[i]!='x':
            dict_REL.update({mnemo:str(REL[i])})          
      i=i+1
#print(dict_DIR)
#print(dict_REL)
# Diccionario particular
particular = {'BCLR':['15','1D','181D'],
              'BRCLR':['13','1F','181F'],
              'BRSET':['12','1E','181E'],
              'BSET':['14','1C','181C'],
              }
#print(dict_EXT)
#print(len(mnemonico_excel))
#print(len(dict_REL))
