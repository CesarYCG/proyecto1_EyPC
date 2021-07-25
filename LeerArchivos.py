import pandas as pd
import xlrd
#############
#Obtención de valores desde excel
#############

archivo_excel = pd.read_excel('INSTRUCCIONES.xls')
#print(archivo_excel.columns)


mnemonico_m = archivo_excel['MNEMONICO'].values
###Obtener valores de opcodes

IMM= archivo_excel['OPCODE1'].values
DIR= archivo_excel['OPCODE2'].values
INDX= archivo_excel['OPCODE3'].values
INDY= archivo_excel['OPCODE4'].values
EXT= archivo_excel['OPCODE5'].values
INH= archivo_excel['OPCODE6'].values
REL= archivo_excel['OPCODE7'].values
###Listas donde se guardaran los menemonicos de acuerdo a su clasificación
valuesIMM={}
valuesDIR={}
valuesINDX={}
valuesINDY={}
valuesEXT={}
valuesINH={}
valuesREL={}
#print(mnemonico_m)
i=0
##Se recorreran los menmonicos y se irán guardando en las listas
for mnemo in mnemonico_m:
      if IMM[i]!='x':
            valuesIMM.update({mnemo:str(IMM[i])})
      if DIR[i]!='x':
            valuesDIR.update({mnemo:str(DIR[i])})
      if INDX[i]!='x':
            valuesINDX.update({mnemo:str(INDX[i])})
      if INDY[i]!='x':
            valuesINDY.update({mnemo:str(INDY[i])})
      if EXT[i]!='x':
            valuesEXT.update({mnemo:str(EXT[i])})
      if INH[i]!='x':
            valuesINH.update({mnemo:str(INH[i])})
      if REL[i]!='x':
            valuesREL.update({mnemo:str(REL[i])})          
      i=i+1
particular = {

              'BCLR':['15','1D','181D'],
              'BRCLR':['13','1F','181F'],
              'BRSET':['12','1E','181E'],
              'BSET':['14','1C','181C'],

              }
#print(valuesEXT)
#print(len(mnemonico_m))
#print(len(valuesREL))
