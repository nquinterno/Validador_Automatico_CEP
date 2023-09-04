## Validador Automàtico de CEP (VAC) Copyright (C) <2022> <Ing. Agrim Nicolás Quinterno>

##--------------------------------------------------------------------------------------------

## Este programa permite Validar de manera Automatica distintos aspectos de los planos de Mensura
## que deban presentarse ante la Subgerencia Operativa de Registro de Mensuras - Gerencia Operativa
## de Catastro Fìsico - DGROC - GCBA, en formato DXF.

## Valida entre otros aspectos:
    ## * Coherencia y completitud y correcta representación de datos indicados en el espacio modelo
    ## * Coherencia entre los elementos representados en el model y los datos asociados del resto del archivo
    ## * Correcta georreferenciación de la parcela mensurada
    ## * Difereniamentre los vertices de la parcela registrada en las basses de datos catastrales y la parcela medida

##--------------------------------------------------------------------------------------------

##Este programa es software libre: puedes redistribuirlo y/o modificar
##bajo los términos de la Licencia Pública General GNU Affero publicada
##por la "Free Software Foundation", ya sea la versión 3 de la
##Licencia, o (a su elección) cualquier versión posterior.
##
##Este programa se distribuye con la esperanza de que sea útil,
##pero SIN NINGUNA GARANTIA; sin siquiera la garantía implícita de
##COMERCIABILIDAD o IDONEIDAD PARA UN FIN DETERMINADO. Ver el
##Licencia pública general GNU Affero para obtener más detalles.
##
##Debería haber recibido una copia de la licencia pública general GNU Affero
##junto con este programa. Si no, consulte <https://www.gnu.org/licenses/>.


from tkinter import*
from tkinter import messagebox, filedialog, ttk
from pandas import DataFrame, read_excel, read_csv
from sys import exit
import ezdxf
from ezdxf import recover
from ezdxf.math.construct2d import is_point_in_polygon_2d, Vec2
import math
import re
import difflib
from json import loads
from requests import get
from geopandas import GeoSeries
from shapely import Polygon, union, difference, area, geometry, Point
from os import path
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


raiz=Tk() #ventana almacenada en variable raiz

s = ttk.Style()

raiz.geometry("800x600")
raiz.resizable(width=True, height=True)

raiz.title('VAC - (Validador Automatico CEP)')

marco1 = Frame(raiz)
marco1.config(width="760",height="80")
marco1.grid(padx=5, pady=5, row = 0, column=0)

marco2 =LabelFrame(raiz,text='Validacion')
marco2.grid(padx=5, pady=1, row = 1, column=0)
marco2.config(bg="white",width="760",height="520")

marco3 = Frame(marco1)
marco3.config(width="200",height="60")
marco3.grid(padx=5, pady=3, row = 0, column=0)

marco4 = Frame(marco1)
marco4.config(width="400",height="60")
marco4.grid(padx=5, pady=3, row = 0, column=1)

marco5 = Frame(marco1)
marco5.config(width="200",height="60")
marco5.grid(padx=5, pady=3, row = 0, column=2)

label = Label(marco4,text="VAC - (Validador Automatico CEP)")
label.configure(font=("Gotham Rounded",8))
label.grid(padx=25, pady=2, row = 0, column=1)

label1 = Label(marco4,text="Subgerencia Operativa de Registro de Mensuras\nGerencia Operativa de Catastro Físico\nDirección General de Registro de Obras y Catastro")
label1.configure(font=("Gotham Rounded",8))
label1.grid(padx=25, pady=2, row = 1, column=1)

tv = ttk.Treeview(marco2, height=20)
tv['columns']=("Nº","Validacion")
tv.column("#0", width="0", stretch="NO")
tv.column("Validacion",anchor="w", width="750")
tv.column("Nº",anchor="w", width="25")
tv.heading("Validacion",text="Validación",anchor="w")
tv.heading("Nº",text="Nº",anchor="w")

# #--- Definicion de variables

pages_IFDOM_text = ""
pages_IFTAM_text = ""
pages_IFFVN_text = ""
doc = ""
last_dir = ""

validaciones = DataFrame()
validaciones2 = DataFrame()
validaciones = read_excel('config_validaciones.xls') #data frame con archivo de Configuración de validaciones xls
validaciones2 = validaciones.drop(['Validacion','Descripcion',],axis='columns') #borra columnas innecesarias del data frame validaciones


# #--- Definicion de variables


# #--- Abre DXF con explorador de windows y lo guarda en la variable DOC ---#


def Abrir_Archivo_dxf():
    global doc
    global validaciones
    global validaciones2
    global comparacion
    global last_dir

    global pages_IFDOM_text
    global pages_IFTAM_text
    global pages_IFFVN_text
    
    pages_IFDOM_text = ""
    pages_IFTAM_text = ""
    pages_IFFVN_text = ""
    doc = ""

    validaciones = DataFrame()
    validaciones2 = DataFrame()
    validaciones = read_excel('config_validaciones.xls') #data frame con archivo de Configuración de validaciones xls
    validaciones2 = validaciones.drop(['Validacion','Descripcion',],axis='columns') #borra columnas innecesarias del data frame validaciones
    
    try:
        if last_dir != "":
            ruta = filedialog.askopenfilename(title="abrir", initialdir=f"{last_dir}")
            doc, auditor = recover.readfile(ruta)
        else:
            ruta = filedialog.askopenfilename(title="abrir", initialdir="C:/")
            doc, auditor = recover.readfile(ruta)
            last_dir = path.abspath(ruta)
        
    except IOError:
        exit(1)

    except ezdxf.DXFStructureError:
        print(messagebox.showerror(message="El archivo selecciondo no es un archivo DXF o el mismo esta corrupto", title="Error"))
        exit(2)

# DXF file can still have unrecoverable errors, but this is maybe just
# a problem when saving the recovered DXF file.

    if auditor.has_errors:
        auditor.print_error_report()


def Abrir_Archivo_IFTAM():
    global pages_IFTAM_text
    global comparacion
    global validaciones
    global last_dir

    try:

        if last_dir != "":
            documento = filedialog.askopenfilename(title="abrir Formulario Mensura", initialdir=f"{last_dir}")
        else:
            documento = filedialog.askopenfilename(title="abrir Formulario Mensura", initialdir="C:/")
            last_dir = path.abspath(documento)
      
        if documento.endswith(".pdf"):
            documento_1 = PdfReader(documento)
            num_pages_doc1 = len(documento_1.pages)
            pages_doc1_text = ""


            for page_num in range(num_pages_doc1):
                pages_doc1_text += (documento_1.pages[page_num]).extract_text()

                if 'FORMULARIO TECNICO ACTOS DE MENSURA' in pages_doc1_text:
                    pages_IFTAM_text = pages_doc1_text

                else:
                    print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Mensura", title="Error"))
            documento_1.stream.close() 
        else:
            print(messagebox.showerror(message="El archivo selecciondo no es un archivo pdf", title="Error"))
    except IOError:
        exit(1)

def Abrir_Archivo_IFFVN():
    global pages_IFFVN_text
    global comparacion
    global validaciones
    global last_dir
    comparacion = DataFrame()
    comparacion = validaciones.drop(['Validacion','Descripcion',],axis='columns')
    
    
    try:

        if last_dir != "":
            documento = filedialog.askopenfilename(title="abrir Formulario Resumen", initialdir=f"{last_dir}")
        else:
            documento = filedialog.askopenfilename(title="abrir Formulario Resumen", initialdir="C:/")
            last_dir = path.abspath(documento)
      
        if documento.endswith(".pdf"):
            documento_1 = PdfReader(documento)
            num_pages_doc1 = len(documento_1.pages)
            pages_doc1_text = "" 

            for page_num in range(num_pages_doc1):
                pages_doc1_text += (documento_1.pages[page_num]).extract_text()

                if 'FORMULARIO DE VALUACION' in pages_doc1_text:
                    pages_IFFVN_text = pages_doc1_text

                else:
                    print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Resumen", title="Error"))
            documento_1.stream.close()            
        else:
            print(messagebox.showerror(message="El archivo selecciondo no es un archivo pdf", title="Error"))

    except IOError:
        exit(1)

def Abrir_Archivo_IFDOM():
    global pages_IFDOM_text
    global comparacion
    global validaciones
    global last_dir
    comparacion = DataFrame()
    comparacion = validaciones.drop(['Validacion','Descripcion',],axis='columns')
    
    try:
        if last_dir != "":
            documento = filedialog.askopenfilename(title="abrir Formulario Dominio", initialdir=f"{last_dir}")
        else:
            documento = filedialog.askopenfilename(title="abrir Formulario Dominio", initialdir="C:/")
            last_dir = path.abspath(documento)
      
        if documento.endswith(".pdf"):
            documento_1 = PdfReader(documento)
            num_pages_doc1 = len(documento_1.pages)
            pages_doc1_text = "" 

            for page_num in range(num_pages_doc1):
                pages_doc1_text += (documento_1.pages[page_num]).extract_text()

                if 'FORMULARIO DE DATOS DE DOMINIO' in pages_doc1_text:
                    pages_IFDOM_text = pages_doc1_text

                else:
                    print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Dominio", title="Error"))
            documento_1.stream.close()            
        else:
            print(messagebox.showerror(message="El archivo selecciondo no es un archivo pdf", title="Error"))

    except IOError:
        exit(1)

def Procesar_Archivo():

    global tv
    global layouts
    global lados_parcelas_l
    global validaciones
    global validaciones2
    global resumen
    global colores
    global last_dir
    global btn_procesar_nuevo

    
    colores = read_csv('colores.csv')

    global objetos_planos
    objetos_planos_df = read_excel('objetos.xls')
    objetos_planos = objetos_planos_df["Objetos"].tolist()

    global sup_parc_poly #superficie de parcelas
    global sup_ces_poly #superficie de cesión
    global sup_mens_poly #superficie de mensura calculada como la suma de parcelas y cesiones
    global parcelas_poly_close #parcelas polilineas cerradas
    global lados_parcelas_l #ladoas de parcela
    global excedentes_poly #poligonos de excedente polilinea
    global mejoras_poly #poligonos de mejoras polilinea
    global cesion_poly #poligonos de cesiones polilinea
    global bloque_caratula #caratulas insertas
    global bloque_car_model #caratulas insertas en el model

    sup_parc_poly = 0
    sup_ces_poly = 0
    sup_mens_poly = 0

    lados_parcelas_l = list()


    if doc != "":
        model = doc.modelspace() #inserta el model espace en la variable model
        layouts = doc.layout_names()
        layouts.remove('Model') # crea una lista con los nombres de los layouts borrando el nombre dle model

        for i in tv.get_children():
            tv.delete(i)
        
        chequeo_archivo()
        chequeo_layers()
        chequeo_bloques()
        chequeo_model()
        chequeo_cotas()
        chequeo_layout()
        georref()
        cur_parcela()
        resumen()


        tv.tag_configure(tagname="error",background = "#FEA9A9")
        tv.tag_configure(tagname="ok",background = "#ADFEA9")
        tv.tag_configure(tagname='NaN',background = "light grey")
        tv.tag_configure(tagname='precaucion',background = "orange")
        
        for i in range (0,len(validaciones2)):
            if  validaciones2.loc[i,'Resultado']== 0:
                tv.insert('',END,values=(i,validaciones2.loc[i,'Observacion']),tags=["ok",])

            elif validaciones2.loc[i,'Resultado'] <0:
                tv.insert('',END,values=(i,validaciones2.loc[i,'Observacion']),tags=["error",])

            elif validaciones2.loc[i,'Resultado'] ==50:
                tv.insert('',END,values=(i,validaciones2.loc[i,'Observacion']),tags=["precaucion",])
            elif validaciones2.loc[i,'Resultado'] ==99:
                tv.insert('',END,values=(i,validaciones2.loc[i,'Observacion']),tags=["NaN",])
            else:
                pass

        verscrlbar = ttk.Scrollbar(marco2, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand = verscrlbar.set)
        verscrlbar.pack(side ='right', fill ='y') 
        
        tv.pack(fill="both", expand=True)

        btn_resumen = Button(marco5,text="Resumen DXF", command=mostrar_resumen)
        btn_resumen.configure(font=("Gotham Rounded",8))
        btn_resumen.grid(padx=5, pady=2, row = 1, column=0)

        btn_descargar = Button(marco5,text="Descargar vectores DXF", command=descargar_dxf)
        btn_descargar.configure(font=("Gotham Rounded",8))
        btn_descargar.grid(padx=5, pady=2, row = 2, column=0)

        btn_pdf = Button(marco5,text="Descargar Resultados en PDF", command=salida_pdf)
        btn_pdf.configure(font=("Gotham Rounded",8))
        btn_pdf.grid(padx=5, pady=2, row = 3, column=0)       

    else:
        print(messagebox.showerror(message="Antes de procesar debe cargar el archivo DXF", title="Error"))
        

abrir_dxf = Button(marco3, text="Abrir DXF", command=Abrir_Archivo_dxf)
abrir_dxf.configure(font=("Gotham Rounded",8))
abrir_dxf.grid(padx=5, pady=2, row = 0, column=0)

abrir_IFTAM = Button(marco3, text="Abrir Form Mensura", command=Abrir_Archivo_IFTAM)
abrir_IFTAM.configure(font=("Gotham Rounded",8))
abrir_IFTAM.grid(padx=5, pady=2, row = 1, column=0)

abrir_IFFVN = Button(marco3, text="Abrir Form Resumen", command=Abrir_Archivo_IFFVN)
abrir_IFFVN.configure(font=("Gotham Rounded",8))
abrir_IFFVN.grid(padx=5, pady=2, row = 2, column=0)

abrir_IFDOM = Button(marco3, text="Abrir Form Dominio", command=Abrir_Archivo_IFDOM)
abrir_IFDOM.configure(font=("Gotham Rounded",8))
abrir_IFDOM.grid(padx=5, pady=2, row = 3, column=0)


##btn_procesar_nuevo.grid_forget()

#--- Abre DXF con explorador de windows y lo guarda en la variable DOC ---#

#--- 2 INICIO Validación del Archivo DXF ---#

#--- 2.1 INICIO  Validación de versión de archivo --#


def chequeo_archivo():

    global doc
    global validaciones2
    global tv
    
    version_arch = doc.header['$ACADVER']
    version_num = int(version_arch.replace("AC",""))
    version_no = ['AC1009','AC1012','AC1014','AC1015']

    if (version_num >= 1032) or (version_num <= 1015):
        validaciones2.loc[0,'Resultado']=-1
        validaciones2.loc[0,'Observacion']='ERROR: Las Versiones de DXF admitidas son 2004, 2007, 2010 y 2013'
    else:
        validaciones2.loc[0,'Resultado']=0
        validaciones2.loc[0,'Observacion']='OK: Versión de Archivo DXF correcta'
        

#--- 2.1 FIN  Validación de versión de archivo --#
        
#--- 2.1 INICIO  Validación de layers --#
        

def chequeo_layers():

    global doc
    global validaciones2
    global tv
    global nom_layers_dxf
    
    #inicio Carga Info de layers de archivo y de plantilla
    Layers_DXF = DataFrame() #crea data frame para almacenar los layers del archivo con su configuración
    nombre_layers,color_layers,linea_layers, grosor_layers = list(), list(), list(), list() #crea listas que tendran datos de los layers del dxf y pasaran al data frame



    for layer in doc.layers:                 ##-- Guarda la configuración de los layers en listas
        nombre_layers.append(layer.dxf.name) ##-- guarda nombre de los layers en una lista
        color_layers.append(layer.dxf.color) ##-- guarda nombre de los layers en una lista
        linea_layers.append(layer.dxf.linetype) ##-- guarda nombre de los layers en una lista
        grosor_layers.append(layer.dxf.lineweight) ##-- guarda nombre de los layers en una lista

    Layers_DXF = DataFrame(list(zip(nombre_layers,color_layers,linea_layers, grosor_layers)), columns = ['Nombre','Color','Tipo_Linea','Grosor_Linea']) #arma data frame con los layers y su configuracion
    
    Layers_DXF = Layers_DXF.sort_values('Nombre', ascending=True) #ordena la tabla de layers del DXF en forma ascdenete para poder comparar con la de la plantilla
    Layers_DXF.reset_index(inplace=True, drop=True) #resetea el indice de la tabla ordenada para poder comparar con la de la plantilla
    plantilla_2 = read_csv('Config_Layers.csv') #data frame con archivo de ocnfiguración de layers csv
    del  nombre_layers,color_layers,linea_layers, grosor_layers ##-- Borra las listas de layers que ya no se usan

    # layer_count_DXF = len(doc.layers) ##-- Cuenta el total de layers del archivo DXF
    # layer_count_plantilla = len(plantilla_2) ##-- Cuenta el total de layers del archivo DXF

    elim_nom_layer = list()
    nom_layers_dxf = Layers_DXF["Nombre"].tolist()
    nom_layers_plant = plantilla_2["Nombre"].tolist()
    band_dxf_plant = list()


    for i in range (0,len(nom_layers_dxf)):      # Elimina los elementos que no son bloques del dxf y correconden al layout, model, etc.
       if '@' in nom_layers_dxf[i]:
            elim_nom_layer.append(nom_layers_dxf[i]) 

    for i in range (0,len(elim_nom_layer)):
        nom_layers_dxf.remove(elim_nom_layer[i])
    
    
    #FIN Carga Info de layers de archivo y de plantilla

    #Inicio Validar Layers

    for layer in nom_layers_plant:
        if layer in nom_layers_dxf:
            band_dxf_plant.append('0')
        else:
            band_dxf_plant.append('-1')

    if '-1' in band_dxf_plant:
        validaciones2.loc[1,'Resultado']=-1
        validaciones2.loc[1,'Observacion']='ERROR: Faltan Layers de la plantilla'

    else:

        validaciones2.loc[1,'Resultado']=0
        validaciones2.loc[1,'Observacion']='OK: Se han detectado todos los layers de la palantilla en el archivo DXF'

    #validar que el layer muro este como no imprimible

                
            
#--- 2.1 FIN Validación de layers --#
            

#--- 2.2 INICIO Validación de bloques --#

def chequeo_bloques ():
    global doc
    nombre_bloque = list()
    global validaciones2

    for block in doc.blocks:                 ##-- Guarda información de los bloques en una lista
            nombre_bloque.append(block.dxf.name) ##-- guarda nombre de los bloques en una lista
    elim_bloque=list()

    for i in range (0,len(nombre_bloque)):      # Elimina los elementos que no son bloques del dxf y correconden al layout, model, etc.
       if '*' in nombre_bloque[i]:
            elim_bloque.append(nombre_bloque[i]) 

    for i in range (0,len(elim_bloque)):
        nombre_bloque.remove(elim_bloque[i])

    Plant_Bloques = read_csv('Config_Bloques.csv') #data frame con archivo de configuración de bloques csv
    Bloques_DXF = DataFrame(list(zip(nombre_bloque)), columns = ['Nombre']) #,'Color','Tipo_Linea','Grosor_Linea']), bloques del archivo dxf

    # Bloques_DXF_count = len(Bloques_DXF)
    # Plant_Bloques_count = len(Plant_Bloques)

    band_bloque_nombre = list()

    for bloque in Bloques_DXF:
        if bloque in Plant_Bloques:
            band_bloque_nombre.append('0')
        else:
            band_bloque_nombre.append('-1')

    if '-1' in band_bloque_nombre:
            validaciones2.loc[2,'Resultado']=-1
            validaciones2.loc[2,'Observacion']='ERROR: Existen más Bloques en el archivo dxf que los admitidos en la plantilla'
            validaciones2.loc[2,'Cetegoría']='Bloques' 

    else:
            validaciones2.loc[2,'Resultado']=0
            validaciones2.loc[2,'Observacion']='OK: Se han detectado todos los Bloques de la palantilla en el archivo DXF'
            validaciones2.loc[2,'Cetegoría']='Bloques' 

    #------>

#--- 2.2 FIN Validación de bloques --#


layer_caratula_1="01-P-PLANO-CARATULA"
layer_cotas_parc_1="03-P-MEDIDAS-PARCELA"

#--- 2.4 INICIO Validación de elementos de Layout --#
    
    #--- 2.4.3 INICIO Validación de Cotas --#

def chequeo_cotas():
##  global layer_cotas_parc_1
    cotas= doc.query('DIMENSION')
    cotas_parc= doc.query('DIMENSION[layer=="03-P-MEDIDAS-PARCELA"]')

    band_cparc_model = list()
    band_cparc_med = list()
    band_cota_lineal = list()
    band_parc_arc = list()

    global lados_parcelas_l
    global validaciones2
    global layer_cota

    layer_cota = list()

    global parcelas_poly_close

    lados_parcelas=0
    
    cotas_parc_lado = list()
    cotas_parc_ang = list()

    for parcela in parcelas_poly_close:
        if parcela.has_arc:
            band_parc_arc.append("1")
        else:
            band_parc_arc.append("0")

        lados_parcelas_l.append(len(parcela))
    

    if len (cotas_parc)>0:

        #verifica que tipo de acotaciones se utilizo para la parcela 162 = angular, 32 = lineal, 33 = alineado, 
        for cota in cotas_parc:

            if cota.dxf.dimtype == 162:
                cotas_parc_ang.append(cota)

            elif (cota.dxf.dimtype == 33) or (cota.dxf.dimtype == 8):
                cotas_parc_lado.append(cota)

            elif (cota.dxf.dimtype == 32):
                band_cota_lineal.append('-1')
                
            else:
                pass


        for i in range (len(lados_parcelas_l)):         #Para todas las parcelas suma la cantidad de lados que tiene para comparar con la cantidad de cotas realizadas 
            lados_parcelas=lados_parcelas+lados_parcelas_l[i]

            
        for cota in cotas_parc:        
            if cota.dxf.paperspace==0:
                band_cparc_model.append('-1')
            else:
                band_cparc_model.append('0')

            if len(cota.dxf.text)==0:
                band_cparc_med.append('0')
            else:
                band_cparc_med.append('-1')

                
        if '-1' in  band_cparc_model:
            validaciones2.loc[3,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[3,'Observacion']="ERROR: Se acotó en el model"
            validaciones2.loc[3,'Cetegoría']='Acotaciones'
        else:
            validaciones2.loc[3,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[3,'Observacion']="OK: Se acoto en el Layout"
            validaciones2.loc[3,'Cetegoría']='Acotaciones'
            
        if '-1' in  band_cparc_med:
            validaciones2.loc[4,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[4,'Observacion']="ERROR: Se modificó el valor real de alguna de las cotas de parcelas"
            validaciones2.loc[4,'Cetegoría']='Acotaciones'
        else:
            validaciones2.loc[4,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[4,'Observacion']="OK: No se han modificado los valores reales de las cotas de parcelas"
            validaciones2.loc[4,'Cetegoría']='Acotaciones'
            
        if (int(lados_parcelas) == len(cotas_parc)):
            validaciones2.loc[5,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[5,'Observacion']="OK: Se acotó correctamente"
            validaciones2.loc[5,'Cetegoría']='Acotaciones'            
        else:
            if "1" in band_parc_arc:
                validaciones2.loc[5,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[5,'Observacion']="OK: Se acotó correctamente"
                validaciones2.loc[5,'Cetegoría']='Acotaciones'   
            else:
                validaciones2.loc[5,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[5,'Observacion']="ERROR:No coinciden el N° de lados de la parcela con el N° de acotaciones aligned realizadas, o no están en el layer '03-P-MEDIDAS-PARCELA'"
                validaciones2.loc[5,'Cetegoría']='Acotaciones'
    else:

        if len(cotas)==0:
            validaciones2.loc[3,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[3,'Observacion']="ERROR: No se uso un Dimensionado para acotar"
            validaciones2.loc[3,'Cetegoría']='Acotaciones'

            validaciones2.loc[4,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[4,'Observacion']="ERROR: No se uso un Dimensionado para acotar"
            validaciones2.loc[4,'Cetegoría']='Acotaciones'

            validaciones2.loc[5,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[5,'Observacion']="ERROR: No se uso un Dimensionado 'Alineado' o 'de arco' para acotar"
            validaciones2.loc[5,'Cetegoría']='Acotaciones'
        else:

            validaciones2.loc[3,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[3,'Observacion']="ERROR: No se Acoto en el layer 03-P-MEDIDAS-PARCELA"
            validaciones2.loc[3,'Cetegoría']='Acotaciones'

            validaciones2.loc[4,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[4,'Observacion']="ERROR: No se Acoto en el layer 03-P-MEDIDAS-PARCELA"
            validaciones2.loc[4,'Cetegoría']='Acotaciones'

            validaciones2.loc[5,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[5,'Observacion']="ERROR: No se Acoto en el layer 03-P-MEDIDAS-PARCELA"
            validaciones2.loc[5,'Cetegoría']='Acotaciones'
            
    
    #--- 2.4.3 FIN Validación de Cotas --#
#--- 2.4 FIN Validación de elementos de Layout --#

#--- 2.5 INICIO Validación de elementos del model --#

def chequeo_model():
    global model
    global lados_parcelas_l
    global lados_parcelas
    global validaciones2
    global colores
    global sup_parc_poly
    global sup_ces_poly
    global sup_mens_poly
    global parcelas_poly_close
    global parcelas_poly
    global colores
    global medidas_dxf

    #--- 2.5.1 INICIO Validación de Parcela--#
    parcelas = doc.modelspace().query('*[layer=="09-M-PARCELA"]')#  Busca las polylineas en el layer PARCELA
    parcelas_poly=list()
    parcelas_poly_close=list()
    band_poly_parc=list()   #lista de banderas para validar todas las entidades del layer parcela sean polilineas
    band_poly_cer_parc=list() #lista de banderas para validar que todas las las polylineas del layer parcela sean cerradas
    band_poly_gro_parc=list()
    band_poly_color_parc=list()
    band_parc_arc = list()
    medidas_dxf = list()
    
##    Calcular la cantidad de lados que tiene la parcela

    
    if len(parcelas): #si hay entindades en el layer patrcela comienza la validacion de las mismas sino arroja error que no hay nada en ese layer
        for parcela in parcelas:
            if parcela.dxftype()!= "LWPOLYLINE": # agrega -1 a la bandera cuando la entidas no es lwpolyline
                if parcela.dxftype()!= "INSERT":
                    band_poly_parc.append('-1')
                else:
                    if parcela.dxf.name != "PARCELA_SURGENTE":
                        #band_poly_parc.append('-1') ver que vandera usar para uando hay un bloque inserto en parcela y no es el bloque de parcela surgente
                        band_poly_parc.append('-1')
                    else:
                        band_poly_parc.append('0')
            else:
                band_poly_parc.append('0') # agrega 0 a la bandera cuando la entidad es lwpolyline
                parcelas_poly.append(parcela)

        if "-1" in band_poly_parc: # si hay un -1 en la bandera arroja error 
            validaciones2.loc[6,'Resultado']=-1
            validaciones2.loc[6,'Observacion']="ERROR: Existen entidades distintas de Polylineas y Bloque de nomenclatura en el Layer 09-M-PARCELA"
            validaciones2.loc[6,'Cetegoría']='Parcela/s'  
        else:
            for parcela in parcelas_poly:
                if parcela.has_arc:
                    band_parc_arc.append("1")
                else:
                    band_parc_arc.append("0")
                if parcela.closed:
                    band_poly_cer_parc.append('0')  # agrega 0 a la bandera cuando la polylinea es cerrada
                    parcelas_poly_close.append(parcela)
                else:
                    band_poly_cer_parc.append('-1') # agrega -1 a la bandera cuando la polylinea es abierta
                
                vertices_p1 = parcela.get_points('xy')
                for i in range(len(vertices_p1)):
                   medidas_dxf.append(round(math.sqrt(((vertices_p1[i][0]-vertices_p1[i-1][0])**2)+((vertices_p1[i][1]-vertices_p1[i-1][1])**2)),2))

            if '-1' in band_poly_cer_parc:
                validaciones2.loc[6,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[6,'Observacion']="ERROR: Se dibujaron polylineas Abiertas en el layer 09-M-PARCELA"
                validaciones2.loc[6,'Cetegoría']='Parcela/s'  

            else:# si no hay un -1 en la bandera sigue validando color y grosor de polylineas.

                validaciones2.loc[6,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[6,'Observacion']="OK: Se dibujaron polylineas Cerradass en el layer 09-M-PARCELA"
                validaciones2.loc[6,'Cetegoría']='Parcela/s'

        if len(parcelas_poly) > 1:
                validaciones2.loc[7,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[7,'Observacion']="ERROR: Se dibujaron más de una polylineas en el layer 09-M-PARCELA"
                validaciones2.loc[7,'Cetegoría']='Parcela/s'

        elif len(parcelas_poly) == 1:
                validaciones2.loc[7,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[7,'Observacion']="OK: Se dibujó una unica polylinea en el layer 09-M-PARCELA"
                validaciones2.loc[7,'Cetegoría']='Parcela/s'

        elif len(parcelas_poly) == 0:
                validaciones2.loc[7,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[7,'Observacion']="ERROR: No se dibujaron polylineas en el layer 09-M-PARCELA"
                validaciones2.loc[7,'Cetegoría']='Parcela/s'       

        for parcela in parcelas:
            if parcela.dxf.color==colores.at[0,'Parcela']:   
                band_poly_color_parc.append('0')
            else:
                band_poly_color_parc.append('-1')

            if parcela.dxf.lineweight==-3:
                band_poly_gro_parc.append('0')
            else:
                band_poly_gro_parc.append('-1')
##                lados_parcelas_l.append(parcela.dxf.count)
                
        if '0' in band_poly_color_parc and '0' in band_poly_gro_parc:
            validaciones2.loc[8,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[8,'Observacion']="OK: Se dibujaron polylineas Cerradas configuradas correctamente en el layer 09-M-PARCELA"
            validaciones2.loc[8,'Cetegoría']='Parcela/s'  

        elif '0' in band_poly_color_parc and '-1' in band_poly_gro_parc:
            validaciones2.loc[8,'Resultado']=-5 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[8,'Observacion']="ERROR: Grosor de polylineas erroneo en layer 09-M-PARCELA debe ser 'Default'"

        elif '-1' in band_poly_color_parc and '0' in band_poly_gro_parc:
            validaciones2.loc[8,'Resultado']=-4 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[8,'Observacion']="ERROR: Color de polylineas erroneo en layer 09-M-PARCELA debe ser Azul"
            validaciones2.loc[8,'Cetegoría']='Parcela/s'  

        elif '-1' in band_poly_color_parc and '-1' in band_poly_gro_parc:
            validaciones2.loc[8,'Resultado']=-3 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[8,'Observacion']="ERROR: Color y grosor de polylineas erroneo en layer 09-M-PARCELA"
            validaciones2.loc[8,'Cetegoría']='Parcela/s'
        
    else:
        
        validaciones2.loc[6,'Resultado']=-1 #si no hay entindades en el layer parcela arroja error de validación
        validaciones2.loc[6,'Observacion']="ERROR: No se ecuentra diibujada la PARCELA en el Layer 09-M-PARCELA"
        validaciones2.loc[6,'Cetegoría']='Parcela/s'

        validaciones2.loc[7,'Resultado']=-1 #si no hay entindades en el layer parcela arroja error de validación
        validaciones2.loc[7,'Observacion']="ERROR: No se ecuentra diibujada la PARCELA en el Layer 09-M-PARCELA"
        validaciones2.loc[7,'Cetegoría']='Parcela/s'

        validaciones2.loc[8,'Resultado']=-1 #si no hay entindades en el layer parcela arroja error de validación
        validaciones2.loc[8,'Observacion']="ERROR: No se ecuentra diibujada la PARCELA en el Layer 09-M-PARCELA"
        validaciones2.loc[8,'Cetegoría']='Parcela/s'


    #--- 2.5.1 FIN Validación de Parcela --#

    #--- 2.5.2 INICIO Validación de Antecedentes--#
    m_manzana = doc.modelspace().query('*[layer=="07-M-MANZANA"]')
    m_calles = doc.modelspace().query('*[layer=="05-M-NOMBRE-DE-CALLE"]')
    band_ant_manzana = list()
    band_ant_text = list()
    band_calles_text = list()

    if len(m_manzana)>0:
        for element in m_manzana:
            if element.dxftype()== "LWPOLYLINE":
                band_ant_manzana.append("0")
            else:
                band_ant_manzana.append("-1")
                if element.dxftype()== "TEXT":
                    band_ant_text.append("0")
    else:
        
            validaciones2.loc[9,'Resultado']=-1
            validaciones2.loc[9,'Observacion']="ERROR: Verifique que haya pegado con coordenadas originales los elementos del dxf de la manzana correspondiente en el layer 07-M-MANZANA"
            validaciones2.loc[9,'Cetegoría']='Antecedente'

    if "0" in band_ant_manzana:
            validaciones2.loc[9,'Resultado']=0
            validaciones2.loc[9,'Observacion']="OK: El layer 07-M-MANZANA no se encuentra vacío"
            validaciones2.loc[9,'Cetegoría']='Antecedente'  

    else:
        
        validaciones2.loc[9,'Resultado']=-1
        validaciones2.loc[9,'Observacion']="ERROR: Verifique que haya pegado con coordenadas originales los elementos del dxf de la manzana correspondiente en el layer 07-M-MANZANA"
        validaciones2.loc[9,'Cetegoría']='Antecedente'


    if len(m_calles)>0:
        for element in m_calles:
            if element.dxftype()== "TEXT":
                band_calles_text.append("0")
            else:
                band_calles_text.append("-1")

        if "-1" in band_calles_text:
            validaciones2.loc[10,'Resultado']=-1
            validaciones2.loc[10,'Observacion']="ERROR:En el layer 05-M-NOMBRES-DE-CALLE deben indicarse los nombres de calle del DXF de la manzana correspondiente con entidad 'TEXT'"
            validaciones2.loc[10,'Cetegoría']='Antecedente'

        else:
            validaciones2.loc[10,'Resultado']=0
            validaciones2.loc[10,'Observacion']="OK: En el layer 05-M-NOMBRES-DE-CALLE se encuentran indicadas solo entidades de 'TEXT'"
            validaciones2.loc[10,'Cetegoría']='Antecedente'
                
    else:
        validaciones2.loc[10,'Resultado']=-1
        validaciones2.loc[10,'Observacion']="ERROR: El layer 05-M-NOMBRES-DE-CALLE está vacío, debe copiarse con coord. originales los elementos del DXF de la manzana correspondiente"
        validaciones2.loc[10,'Cetegoría']='Antecedente'
 
    #--- 2.5.2 INICIO Validación de Antecedentes--#
    #--- 2.5.3 INICIO Validación de Excedente--#
    excedentes = doc.modelspace().query('*[layer=="11-M-EXCEDENTE"]')#  Busca las polylineas en el layer EXCEDENTE

    band_poly_exc=list()   #lista de banderas para validar todas las entidades del layer excedente sean polilineas
    band_poly_cer_exc=list() #lista de banderas para validar que todas las las polylineas del layer parcela sean cerradas
    band_poly_gro_exc=list()
    band_poly_color_exc=list()

    global excedentes_poly
    global excedentes_poly_close


    excedentes_poly = list()
    excedentes_poly_close = list()


    if len(excedentes): #si hay entindades en el layer patrcela comienza la validacion de las mismas sino arroja error que no hay nada en ese layer
        for excedente in excedentes:
            if excedente.dxftype()!= "LWPOLYLINE": # agrega -1 a la bandera cuando la entidas no es lwpolyline
                band_poly_exc.append('-1')
            else:
                band_poly_exc.append('0') # agrega 0 a la bandera cuando la entidad es lwpolyline

        if "-1" in band_poly_exc: # si hay un -1 en la bandera arroja error 
            validaciones2.loc[11,'Resultado']=-1
            validaciones2.loc[11,'Observacion']="ERROR: Existen entidades distintas de Polylineas en el Layer EXCEDENTE"
            validaciones2.loc[11,'Cetegoría']='Parcela/s'  
        else:

            for excedente in excedentes:
                if excedente.dxftype()== "LWPOLYLINE":
                    if excedente.closed:
                        band_poly_cer_exc.append('0')  # agrega 0 a la bandera cuando la polylinea es cerrada
                        excedentes_poly_close.append(excedente)
                    else:
                        band_poly_cer_exc.append('-1') # agrega -1 a la bandera cuando la polylinea es abierta
                else:
                    pass
                
            if '-1' in band_poly_cer_exc:
                    validaciones2.loc[11,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                    validaciones2.loc[11,'Observacion']="ERROR: Se dibujaron polylineas Abiertas en el layer EXCEDENTE"
                    validaciones2.loc[11,'Cetegoría']='Parcela/s'
            else:
                validaciones2.loc[11,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[11,'Observacion']="OK: Se dibujaron polylineas Cerradas en el layer EXCEDENTE"
                validaciones2.loc[11,'Cetegoría']='Parcela/s'#si la polylinea es cerrada sigue validando que tengan el color y grosor bylayer

                
        for excedente in excedentes: 
            if excedente.dxf.color==7:   
                band_poly_color_exc.append('0')
            else:
                band_poly_color_exc.append('-1')

            if excedente.dxf.lineweight==-3:
                        band_poly_gro_exc.append('0')
            else:
                band_poly_gro_exc.append('-1')

        if '0' in band_poly_color_exc and '0' in band_poly_gro_exc:
            validaciones2.loc[12,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[12,'Observacion']="OK: Se dibujaron polylineas Cerradas configuradas correctamente en el layer EXCEDENTE"
            validaciones2.loc[12,'Cetegoría']='Parcela/s'
            
        elif '0' in band_poly_color_exc and '-1' in band_poly_gro_exc:
            validaciones2.loc[12,'Resultado']=-5 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[12,'Observacion']="ERROR: Grosor de polylineas erroneo en layer EXCEDENTE"
            validaciones2.loc[12,'Cetegoría']='Parcela/s'
            
        elif '-1' in band_poly_color_exc and '0' in band_poly_gro_exc:
            validaciones2.loc[12,'Resultado']=-4 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[12,'Observacion']="ERROR: Color de polylineas erroneo en layer EXCEDENTE"
            validaciones2.loc[12,'Cetegoría']='Parcela/s'
            
        elif '-1' in band_poly_color_exc and '-1' in band_poly_gro_exc:
            validaciones2.loc[12,'Resultado']=-3 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[12,'Observacion']="ERROR: Color y grosor de polylineas erroneo en layer EXCEDENTE"
            validaciones2.loc[12,'Cetegoría']='Parcela/s'
        ## INICIO VERIFICACIÓN EXCEDENTE ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.

        excedentes_poly= excedentes.query('LWPOLYLINE')
        parcelas_poly= parcelas.query('LWPOLYLINE')
        band_exc_dentro=list() #inicia bandera de control si cada uno de los excedentes estan dentro de una parcela
        for excedente in excedentes_poly: #reccorre poligonos de excedentes
            vertices_e1 = excedente.get_points('xy') #para cada excedente obtiene los vertices y los prepara para la función de control
            vertices_e2 = Vec2.list(vertices_e1)
            band_parc_dentro=list() #bandera que controla si el excedente x esta dentro de laguna de las parcelas
            for parcela in parcelas_poly: #fijado un excedente reccorre poligonos de parcelas para comparar vertices
                #Para que la funcion offset no tire error por vectores nulos al haber vertices repetidos se recorre la polilinea y solo se guardan en la lista vertices_p1 si ya esta repetido
                # vert_unicos_parc = set()
                vertices_p1 = list()
                for vert in parcela.vertices():
                    if vert in vertices_p1:
                        pass
                    else:
                        vertices_p1.append(vert)
                #vertices_p1 = parcela.get_points('xy')  #para cada parcela obtiene los vertices y los prepara para la función de control
                vertices_p2 = Vec2.list(vertices_p1)
                vertices_p3 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=-0.01, closed=True))
                vertices_p4 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=0.01, closed=True))
                band_vert_dentro=list() #inicia bandera que valida si los vertices del excedente caen dentro de el polig. de parcela

                for i in range (0,len(vertices_e2)): 
                    
                    if ezdxf.math.is_point_in_polygon_2d(vertices_e2[i],vertices_p3,abs_tol=1e-3)==-1: #validación de vertices arroja -1 si cae fuera, 0 si cae en los limites y 1 si cae dentro
                        if ezdxf.math.is_point_in_polygon_2d(vertices_e2[i],vertices_p4,abs_tol=1e-3)==-1:
                            band_vert_dentro.append('-1')
                        else:
                            band_vert_dentro.append('0')
                    else:
                        band_vert_dentro.append('0')
                        
                if '-1' in band_vert_dentro:
                    band_parc_dentro.append('-1')
                else:
                    band_parc_dentro.append('0')
                del band_vert_dentro
                    
            if '0' in band_parc_dentro:
                band_exc_dentro.append('0')
                
            else:
                band_exc_dentro.append('-1')

            del band_parc_dentro

        if '-1' in band_exc_dentro:
            validaciones2.loc[13,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[13,'Observacion']="ERROR: Existe al menos un excedente fuera de la o las Parcelas mensuradas"
            validaciones2.loc[13,'Cetegoría']='Parcela/s'
        else:
            validaciones2.loc[13,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
            validaciones2.loc[13,'Observacion']="OK: El o los excedentes se encuentran completamente dentro de la/las Parcelas Mensuradas"
            validaciones2.loc[13,'Cetegoría']='Parcela/s'

            ## FIN VERIFICACIÓN EXCEDENTE ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.
    else:
        
        validaciones2.loc[11,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[11,'Observacion']="OK: Validación de excedente no corresponde por encontrase el layer vacío, verifique que no exista uno para la parcela medida"
        validaciones2.loc[11,'Cetegoría']='Parcela/s'

        validaciones2.loc[12,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[12,'Observacion']="OK: Validación de excedente no corresponde por encontrase el layer vacío, verifique que no exista uno para la parcela medida"
        validaciones2.loc[12,'Cetegoría']='Parcela/s'

        validaciones2.loc[13,'Resultado']=99 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
        validaciones2.loc[13,'Observacion']="OK: Validación de excedente no corresponde por encontrase el layer vacío, verifique que no exista uno para la parcela medida"
        validaciones2.loc[13,'Cetegoría']='Parcela/s'
     

    #--- 2.5.2 FIN Validación de Excedente --#

    #--- 2.5.3 INICIO Validación de Bloque NOmenclatura Parcela --#

    #Validar que se encuentre inserto y completo el bloque "PARCELA_VIGENTE" tantas veces como poligonos cerrados de parcela haya. 

    bloque_PARCELA_SURGENTE = doc.modelspace().query('INSERT[name=="PARCELA_SURGENTE"]')
    patron_parc = re.compile('(^([0-9]{3})|([0-9]{3}[a-z]{1}))$') #patron para validar el formato de la parcela escrito en el bloque mensura
    nom_parc_list=list()
    
    #valida que haya la misma cantidad de bloques de parcela insertos en el dxf que la cantidad de parcelas del layer parcelas.    

    if len(bloque_PARCELA_SURGENTE)==1:
            validaciones2.loc[14,'Resultado']=0
            validaciones2.loc[14,'Observacion']='OK: Exite inserto un unico bloque "PARCELA_SURGENTE"'
            validaciones2.loc[14,'Cetegoría']='Bloques'

            ban_bparc_comp=list()
            band_nom_parc = list()
                
            for bloque in (bloque_PARCELA_SURGENTE):
                    for attrib in bloque.attribs:
                        if attrib.dxf.tag=="NPARC":
                            nom_parc_list.append(attrib.dxf.text)
                            if attrib.dxf.text == None:
                                ban_bparc_comp.append(-1)
                            else:
                                ban_bparc_comp.append(0)

                    if -1 in ban_bparc_comp:
                        validaciones2.loc[15,'Resultado']=-1
                        validaciones2.loc[15,'Observacion']='ERROR: El o los bloques "PARCELA_SURGENTE" estan vacíos'
                        validaciones2.loc[15,'Cetegoría']='Bloques' 

                    else:

                            #validar que la nomenclatura del bloque Parc_vig tegnga elformato correcto 000a#

                        for i in nom_parc_list:
                            band_nom_parc.append(patron_parc.match(i))                                            
                    
                        if None in band_nom_parc:
                            validaciones2.loc[15,'Resultado']=-1
                            validaciones2.loc[15,'Observacion']='ERROR: La nomenclatura indicada en el de los bloque "PARCELA_SURGENTE" no respeta el formato 000a'
                            validaciones2.loc[15,'Cetegoría']='Bloques'
                        else:
                            validaciones2.loc[15,'Resultado']=0
                            validaciones2.loc[15,'Observacion']='OK: La nomenclatura indicada el bloque "PARCELA_SURGENTE" respeta el formato 000a'
                            validaciones2.loc[15,'Cetegoría']='Bloques'

    elif len(bloque_PARCELA_SURGENTE)>1:
            validaciones2.loc[14,'Resultado']=-2
            validaciones2.loc[14,'Observacion']='ERROR: Exite más de un boque "PARCELA_SURGENTE" inserto'
            validaciones2.loc[14,'Cetegoría']='Bloques'

            validaciones2.loc[15,'Resultado']=-1
            validaciones2.loc[15,'Observacion']='ERROR: Exite más de un boque "PARCELA_SURGENTE" inserto'
            validaciones2.loc[15,'Cetegoría']='Bloques'

    elif len(bloque_PARCELA_SURGENTE)==0:
            validaciones2.loc[14,'Resultado']=-1
            validaciones2.loc[14,'Observacion']='ERROR: No se ha insertado el bloque "PARCELA_SURGENTE"'
            validaciones2.loc[14,'Cetegoría']='Bloques'

            validaciones2.loc[15,'Resultado']=-1
            validaciones2.loc[15,'Observacion']='ERROR: No se ha insertado el bloque "PARCELA_SURGENTE"'
            validaciones2.loc[15,'Cetegoría']='Bloques'

 #valida que haya la misma cantidad de bloques de parcela insertos en el dxf que la cantidad de parcelas del layer parcelas

        #Validar que el bloque de nomenclatura este en el model y adentro de una parcela#   

    else:
        validaciones2.loc[14,'Resultado']=-1
        validaciones2.loc[14,'Observacion']='Error: No se encuentra inserto el bloque "PARCELA_SURGENTE" por cada una de las parcelas que surgen o se mantienen vigentes con este plano'
        validaciones2.loc[14,'Cetegoría']='Bloques'

        validaciones2.loc[15,'Resultado']=99
        validaciones2.loc[15,'Observacion']='ERROR: No se puede validar el bloque "PARCELA_SURGENTE" dado que no se encuentra inserto'
        validaciones2.loc[15,'Cetegoría']='Bloques'

            
    #--- 2.5.3 FIN Validación de Bloque Nomenclatura Parcela --#  


    #--- 2.5.4 INICIO Validación de MEJORAS--#
    global mejoras_poly
    global nom_layers_dxf
    global forms
    global forms_empadronados
    global forms_descubiertos
    global forms_vacios
    global layers_mejoras
    global layers_mejoras_1
    global layers_mejoras_spb
    global piso_con_mejoras
    global band_form_polig

    global info_form_nuevo
    global info_form_emp
    global info_form_sin_info
    global info_form_desc
    global info_form_vacio
    global info_form_muchos_form

    global sup_cub_dxf
    global sup_semicub_dxf
    global sup_descub_dxf
    global sup_descont_dxf
    global mejora_piso

    global band_mejora_cub_arc_0
    global band_mejora_semi_arc_0
    global band_mejora_desc_arc_0
    global band_mejora_emp_arc_0
    global band_mejora_nueva_arc_0

    
    info_form_nuevo = list()
    info_form_emp = list()
    info_form_sin_info = list()
    info_form_desc = list()
    info_form_vacio = list()
    info_form_muchos_form = list()
    #info_form = list()
    mejoras = doc.modelspace().query('*[layer ? ".*-SUP"]') #  Busca las polylineas en los layers que finalizan con -SUP
    band_poly_mej=list()   #lista de banderas para validar todas las entidades del layer excedente sean polilineas
    band_poly_cer_mej=list() #lista de banderas para validar que todas las las polylineas del layer parcela sean cerradas
    band_poly_gro_mej=list()
    band_poly_color_mej=list()
    forms = list()
    forms_empadronados = list()
    forms_descubiertos = list()
    forms_vacios = list()
    mejoras_poly = list()
    layers_mejoras_0 = list()
    layers_mejoras_1 = list()
    layers_mejoras = list()
    band_mej_form_piso = list() #bandera que captura la validacion de cntidad de polilineas y formularios por piso
    piso_con_mejoras_0 = list()
    piso_con_mejoras = list()
    patron_polig = re.compile('^[0-9]*$')
    band_letra_form = list()
    band_form_polig = list()
    mejora_piso = list()

    forms_polig = list()
    forms_polig_sorted = list()
    forms_N_forms =list()
    forms_T_forms =list()
    band_T_forms = list()
    band_N_forms = list()
    band_1_polig = list() #bandera que guarda si el primer numero d elos poligonos es 1
    band_correl_polig = list() #bandera que guarda si los valores de numero d epoligonos son correlativos
    band_correl_polig_2 = list() #bandera que guarda lo mismo que la nterior pero sin el primer valor
    #patron_polig = re.compile('^[0-9]*$')
    #band_letra_form = list()
    sup_cub_dxf = list()
    sup_semicub_dxf = list()
    sup_descub_dxf = list()
    sup_descont_dxf = list()

    for layer in nom_layers_dxf:  #recorre todos los layers del dxf y si tiene la leyenda -sup en el nombre lo guarda en una lista d enombres de layers de superficie
        if "-SUP" in layer:
            layers_mejoras_0.append(layer)
            if "M-M-PB-SUP" in layer:
                pass
            else:
                layers_mejoras_1.append(layer)
        else:
            pass

    layers_mejoras = list(set(layers_mejoras_0)) #Arma una lista de valores unicos con los nombres de los layers de superficie

    layers_mejoras_spb = list(set(layers_mejoras_1)) #Arma una lista de valores unicos con los nombres de los layers de superficie sin el de planta baja
    
    #inicializacion de banderas para determinar si los distintos tipos de superficies tienen arco
    band_mejora_cub_arc_0 = list()
    band_mejora_semi_arc_0 = list()
    band_mejora_desc_arc_0 = list()
    band_mejora_emp_arc_0 = list()
    band_mejora_nueva_arc_0 = list()
    band_mejora_vacio_arc_0 = list()
    
    for layer in layers_mejoras:
        consulta = f'layer=="{layer}"'
        mejora_piso = doc.modelspace().query(f'LWPOLYLINE[{consulta}]') #renombrar por mejora_piso_0
        form_piso = doc.modelspace().query(f'INSERT[{consulta}]')
        if len(mejora_piso)>0:
            piso_con_mejoras_0.append(layer)
        else:
            pass
        band_mejora_arc = list()
        #codigo para verificar que un form este inserto dentro de un poligono

        band_form_dentro = list()
        

        form_piso_sueltos = form_piso[:]

        for i in range (len(mejora_piso)):
            form_dentro_mejora = list()
            form_dentro_mejora_2 = list()
            form_dentro_mejora_3 = list()
            mejora_piso_comp = mejora_piso[:]
            mejora_piso_comp.pop(i)

            vertices_mp0 = list()
            for vert in mejora_piso[i].vertices():
                if vert in vertices_mp0:
                    pass
                else:
                    vertices_mp0.append(vert)
            
            #vertices_mp0 = mejora_piso[i].get_points('xy') #para cada mejora obtiene los vertices y los prepara para la función de control
            vertices_mp1 = Vec2.list(vertices_mp0)
            vertices_mp12 = list(ezdxf.math.offset_vertices_2d(vertices_mp1,offset=-0.01, closed=True))
            vertices_mp13 = list(ezdxf.math.offset_vertices_2d(vertices_mp1,offset=0.01, closed=True))

            mejora_adentro_2 =list ()
            band_mej_mej_dentro_2 = list()

            band_mejora_arc = list()
            band_mejora_adentro_arc = list()

            # Inicio Calcula la superficie del poligono de la mejora dependiendo si tiene arco o no
            if mejora_piso[i].has_arc:
                mejora_explode_2 = mejora_piso[i].virtual_entities()
                for entity in mejora_explode_2:
                    entity_01 = list()
                    entity_02 = list()
                    if entity.dxftype() == "ARC":
                        entity_01.append(entity.flattening(0.00000001))

                        for ent in entity_01:
                            points = list(ent)
                            for p in points:  
                                entity_02.append((p.x, p.y))
                    else:
                        entity_02.append((entity.dxf.start.x, entity.dxf.start.y))
                            
                sup_mejora_0 = round(ezdxf.math.area(Vec2(punto) for punto in entity_02),2)
                band_mejora_arc.append("1")
            else:
                sup_mejora_0 = round(ezdxf.math.area(Vec2.list(mejora_piso[i].get_points('xy'))),2)
            
            # FIN Calcula la superficie del poligono de la mejora dependiendo si tiene arco o no

            # INICIO detecta las mejoras que se encuentran dibujadas dentro de la mejora madre
            
            for mejora in mejora_piso_comp:
                vertices_mp2 = mejora.get_points('xy') #para cada mejora obtiene los vertices y los prepara para la función de control
                vertices_mp3 = Vec2.list(vertices_mp2)
                
                band_vert_mej_dentro_2 = list()
                
                for vertice in vertices_mp3:
                    if ezdxf.math.is_point_in_polygon_2d(vertice,vertices_mp12,abs_tol=1e-3)==-1: #validación de vertices arroja -1 si cae fuera, 0 si cae en los limites y 1 si cae dentro
                        if ezdxf.math.is_point_in_polygon_2d(vertice,vertices_mp13,abs_tol=1e-3)==-1:
                            band_vert_mej_dentro_2.append("-1")
                        else:
                            band_vert_mej_dentro_2.append("0")
                    else:
                        band_vert_mej_dentro_2.append("0")
                
                if "-1" in band_vert_mej_dentro_2:
                    band_mej_mej_dentro_2.append("-1")
                else:
                    band_mej_mej_dentro_2.append("0")
                    mejora_adentro_2.append(mejora)
            
            # FIN detecta las mejoras que se encuentran dibujadas dentro de la mejora madre


            # INICIO Calcula la superficie de las mejoras Hijas dependiendo si tienen arco o no
            # Además de los formularios dentro de la mejora madre detecta los que estan en las hijas, para identificar cual es el formulario de la mejora madre

            
            if len(mejora_adentro_2)>0:
                #genera poligono de mejora madre
                poligono_madre = Polygon(list(mejora_piso[i].get_points('xy'))) #para cada mejora obtiene los vertices y los prepara para la función de control
                 #genera poligono de mejora hija 1 para iniciar la union de mejoras hijas para luego restar a la madre
                poligono_agujero = Polygon(list(mejora_adentro_2[0].get_points('xy')))
                for mejora in mejora_adentro_2:
                    #va uniendo los poligonos de las mejoras hijas
                    mejora_poligon = Polygon(list(mejora.get_points('xy')))
                    poligono_agujero = union(poligono_agujero,mejora_poligon)
                    if mejora.has_arc:
                        band_mejora_adentro_arc.append("1")
                #resta a la mejora madre el agujero de las mejoras hijas
                poligono_diference = difference(poligono_madre,poligono_agujero)
                sup_mejora_descont_2 = area(poligono_diference) #calcula superficie del poligono despues de todas las restas

                for form in form_piso: #detecta todos los formularios que caen dentro del poligono de mejora madre
                    vertice_k = form.dxf.insert
                    if ezdxf.math.is_point_in_polygon_2d(vertice_k,vertices_mp1,abs_tol=1e-3)==-1:
                        pass
                    else:
                        form_dentro_mejora_2.append(form)
                
                if len(form_dentro_mejora_2)>0:
                    for form1 in form_dentro_mejora_2:
                        band_form_polig_dentro = list()
                        vertice_f = form1.dxf.insert
                        for mejora in mejora_adentro_2:
                            vertices_md0 = mejora.get_points('xy') #para cada mejora obtiene los vertices y los prepara para la función de control
                            vertices_md1 = Vec2.list(vertices_md0)

                            if ezdxf.math.is_point_in_polygon_2d(vertice_f,vertices_md1,abs_tol=1e-3)==-1:
                                band_form_polig_dentro.append("0")
                            else:
                                band_form_polig_dentro.append("-1")
                        if "-1" in band_form_polig_dentro:
                            pass
                        else:
                            form_dentro_mejora_3.append(form1) #formularios que caen fuera de todas las mejoras hijas pero dentro de la madre

                    if len(form_dentro_mejora_3) == 1:
                        if form_dentro_mejora_3[0].dxf.name == "form":
                            for attrib in form_dentro_mejora_3[0].attribs:
                                if attrib.dxf.tag=="Nº_POLIG.":
                                    if len(attrib.dxf.text)==0:
                                        band_form_polig.append('-1')
                                    else:
                                        band_form_polig.append('0')
                                        if patron_polig.match(attrib.dxf.text):
                                            form_polig = (int(attrib.dxf.text))
                                        else:
                                            pass
                        
                                elif attrib.dxf.tag=="TIPO_FORM":
                                    if len(attrib.dxf.text)==0:
                                        band_T_forms.append('-1')
                                    else:
                                        band_T_forms.append('0')
                                        if patron_polig.match(attrib.dxf.text):
                                            form_tipo = (int(attrib.dxf.text))
                                        else:
                                            pass
                    
                                elif attrib.dxf.tag=="Nº_FORM":
                                    if len(attrib.dxf.text)==0:
                                        band_N_forms.append('-1')
                                    else:
                                        band_N_forms.append('0')
                                        if patron_polig.match(attrib.dxf.text):
                                            form_numero = (int(attrib.dxf.text))
                                        else:
                                            pass
                                else:
                                    pass

                            info_form_nuevo.append({"form":f"{form_tipo}/{form_numero}","polig":f"{form_polig}","sup":f"{sup_mejora_descont_2}"})
                            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                                band_mejora_nueva_arc_0.append("1")
                            else:
                                pass
                        elif form_dentro_mejora_3[0].dxf.name == "form_empadronado":
                            info_form_emp.append(sup_mejora_descont_2)
                            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                                band_mejora_emp_arc_0.append("1")
                            else:
                                pass
                        
                        elif form_dentro_mejora_3[0].dxf.name == "form_descubierto":
                            info_form_desc.append(sup_mejora_descont_2)


                        elif form_dentro_mejora_3[0].dxf.name == "form_vacio":
                            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                                info_form_vacio.append(sup_mejora_descont_2)
                                band_mejora_vacio_arc_0.append("1")
                            else:
                                pass
                        else:
                            pass
                    
                    elif len(form_dentro_mejora_3) == 0:
                        info_form_sin_info.append(sup_mejora_descont_2)
                    
                    else:
                        info_form_muchos_form.append(sup_mejora_descont_2)


                else:
                    pass

            else:
                sup_mejora_descont_2 = sup_mejora_0
                
                for form in form_piso:
                    vertice_i = form.dxf.insert
                    for attrib in form.attribs:
                        if attrib.dxf.tag=="Nº_POLIG.":
                            if len(attrib.dxf.text)==0:
                                band_form_polig.append('-1')
                            else:
                                band_form_polig.append('0')
                                if patron_polig.match(attrib.dxf.text):
                                    form_polig = (int(attrib.dxf.text))
                                else:
                                    pass
                
                        elif attrib.dxf.tag=="TIPO_FORM":
                            if len(attrib.dxf.text)==0:
                                band_T_forms.append('-1')
                            else:
                                band_T_forms.append('0')
                                if patron_polig.match(attrib.dxf.text):
                                    form_tipo = (int(attrib.dxf.text))
                                else:
                                    pass
            
                        elif attrib.dxf.tag=="Nº_FORM":
                            if len(attrib.dxf.text)==0:
                                band_N_forms.append('-1')
                            else:
                                band_N_forms.append('0')
                                if patron_polig.match(attrib.dxf.text):
                                    form_numero = (int(attrib.dxf.text))
                                else:
                                    pass
                        else:
                            pass
                    if ezdxf.math.is_point_in_polygon_2d(vertice_i,vertices_mp1,abs_tol=1e-3)==-1:
                        pass
                    else:
                        form_dentro_mejora.append(form)
                
                if len(form_dentro_mejora) == 1:
                    if form_dentro_mejora[0].dxf.name == "form":
                        info_form_nuevo.append({"form":f"{form_tipo}/{form_numero}","polig":f"{form_polig}","sup":f"{sup_mejora_descont_2}"})
                        if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                            band_mejora_nueva_arc_0.append("1") #bandera para no observar diferencia de superficie de formulario y dxf cuando el poligono tiene arco (porque lo calcula mal el algoritmo)
                        else:
                            pass
                    elif form_dentro_mejora[0].dxf.name == "form_empadronado":
                        info_form_emp.append(sup_mejora_descont_2)
                        if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                            band_mejora_emp_arc_0.append("1") #bandera para no observar diferencia de superficie de formulario y dxf cuando el poligono tiene arco (porque lo calcula mal el algoritmo)
                        else:
                            pass
                             #bandera para no observar diferencia de superficie de formulario y dxf cuando el poligono tiene arco (porque lo calcula mal el algoritmo)

                    elif form_dentro_mejora[0].dxf.name == "form_descubierto":
                        info_form_desc.append(sup_mejora_descont_2)


                    elif form_dentro_mejora[0].dxf.name == "form_vacio":
                        info_form_vacio.append(sup_mejora_descont_2)
                        if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                            band_mejora_vacio_arc_0.append("1")
                        else:
                            pass
                    else:
                        pass
                elif len(form_dentro_mejora) == 0:
                    info_form_sin_info.append(sup_mejora_descont_2)

                else:
                    info_form_muchos_form.append(sup_mejora_descont_2)

            #sup_mejora_descont_2 = round(ezdxf.math.area(Vec2.list(mejora_piso[i].get_points('xy'))),2) - sup_mejora_dentro_2

            if mejora_piso[i].dxf.color==1:
                sup_cub_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==2 or mejora_piso[i].dxf.color==4:
                sup_semicub_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==3 or mejora_piso[i].dxf.color==5:
                sup_descub_dxf.append(sup_mejora_descont_2)
            elif mejora_piso[i].dxf.color==32:
                sup_descont_dxf.append(sup_mejora_descont_2)
            else:
                pass

            if len(band_mejora_arc) or len(band_mejora_adentro_arc):
                if mejora_piso[i].dxf.color==1:
                    band_mejora_cub_arc_0.append("1")
                elif mejora_piso[i].dxf.color==2 or mejora_piso[i].dxf.color==4:
                    band_mejora_semi_arc_0.append("1")
                elif mejora_piso[i].dxf.color==3 or mejora_piso[i].dxf.color==5:
                    band_mejora_desc_arc_0.append("1")
                elif mejora_piso[i].dxf.color==32:
                    band_mejora_vacio_arc_0.append("1")
                else:
                    pass
            else:
                pass
        
    if '-1' in band_form_dentro:
        validaciones2.loc[16,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[16,'Observacion']="Error: Algun bloque de formulario no se encuentra inserto dentro del poligono de superficie al que pertenece"
        validaciones2.loc[16,'Cetegoría']='Mejoras'
        
        
    else:
        validaciones2.loc[16,'Resultado']=0 
        validaciones2.loc[16,'Observacion']="Ok: Los bloques de formularios se encuentran insertos dentro de los poligono de superficie a los que pertenecen"
        validaciones2.loc[16,'Cetegoría']='Mejoras'
        
    del band_form_dentro


    if len(mejora_piso)==len(form_piso): #evalua por piso que haya la misma cantidad de polilineas de mejoras que bloques de fomrularios
        band_mej_form_piso.append("0")
    else:
        band_mej_form_piso.append("-1")

    piso_con_mejoras = list(set(piso_con_mejoras_0))

    if "-1" in band_mej_form_piso:
        validaciones2.loc[17,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[17,'Observacion']="Error: En alguno de los pisos difiere la cantidad de polilineas cerradas que bloques de formulario insertos"
        validaciones2.loc[17,'Cetegoría']='Mejoras'
        
    else:
        validaciones2.loc[17,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[17,'Observacion']="Ok: En todos los pisos existe la misma cantidad de polilineas cerradas de superficies que bloques de formulario insertos"
        validaciones2.loc[17,'Cetegoría']='Mejoras'


    patron_layer_sup = re.compile('^M-M-((PB-SUP)|([0-9]{2}(E|P|S)-SUP))$')

    #patron_layout_cep = re.compile('(^([0-9]{3})-(([0-9]{3})|([0-9]{3}[A-Z]{1}))-(([0-9]{3})|([0-9]{3}[a-z]{1})|(000[A-Z]{1})))$')
    
    band_layer_sup = list()

    for layer in layers_mejoras:

        if (patron_layer_sup.match(layer)):
            band_layer_sup.append('0')
        else:
            band_layer_sup.append('-1')

    if "-1" in band_layer_sup:
        validaciones2.loc[18,'Resultado']=-1
        validaciones2.loc[18,'Observacion']="Error: Alguno de los Layers de Superficies no se ha creado con el nombre correcto"
        validaciones2.loc[18,'Cetegoría']='Mejoras'
    else:
        validaciones2.loc[18,'Resultado']=0
        validaciones2.loc[18,'Observacion']="Ok: Los layers de superficies poseen el formato correcto en el nombre"
        validaciones2.loc[18,'Cetegoría']='Mejoras'
        
    if len(mejoras): #si hay entindades en el layer mejoras comienza la validacion de las mismas sino arroja error que no hay nada en ese layer
        for mejora in mejoras:
            if mejora.dxftype()!= "LWPOLYLINE": # agrega -1 a la bandera cuando la entidas no es lwpolyline

                if mejora.dxftype()!= "INSERT":
                    band_poly_mej.append('-1')
                    
                else:
                    if mejora.dxf.name == "form":
                        band_poly_mej.append('0')
                        forms.append(mejora)
                        
                    elif mejora.dxf.name == "form_empadronado":
                        band_poly_mej.append('0')
                        forms_empadronados.append(mejora)

                    elif mejora.dxf.name == "form_descubierto":
                        band_poly_mej.append('0')
                        forms_descubiertos.append(mejora)
                    
                    elif mejora.dxf.name == "form_vacio":
                        band_poly_mej.append('0')
                        forms_vacios.append(mejora)
                        
                    elif mejora.dxf.name != "form" or mejora.dxf.name != "form_empadronado" or mejora.dxf.name != "form_descubierto" or mejora.dxf.name != "form_vacio":
                        band_poly_mej.append('-2')

            else:
                band_poly_mej.append('0') # agrega 0 a la bandera cuando la entidad es lwpolyline
                mejoras_poly.append(mejora)


        if "-1" in band_poly_mej or "-2" in band_poly_mej: # si hay un -1 en la bandera arroja error 
            validaciones2.loc[19,'Resultado']=-1
            validaciones2.loc[19,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de "-SUP"'
            validaciones2.loc[19,'Cetegoría']='Mejoras'

            validaciones2.loc[20,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones2.loc[20,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de  "-SUP"'
            validaciones2.loc[20,'Cetegoría']='Mejoras'

            validaciones2.loc[21,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones2.loc[21,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de "-SUP"'
            validaciones2.loc[21,'Cetegoría']='Mejoras'

            validaciones2.loc[22,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones2.loc[22,'Observacion']='Error: Existen entidades distintas de Polylineas o bloque form / form_empadronado en alguno de los layers de "-SUP"'
            validaciones2.loc[22,'Cetegoría']='Mejoras'

        else:           
                
            for mejora in mejoras_poly:
                if mejora.closed:
                    band_poly_cer_mej.append('0')  # agrega 0 a la bandera cuando la polylinea es cerrada
                    
                else:
                    band_poly_cer_mej.append('-1') # agrega -1 a la bandera cuando la polylinea es abierta
            
            if '-1' in band_poly_cer_mej:
                validaciones2.loc[19,'Resultado']=-2 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[19,'Observacion']="Error: Se dibujaron polylineas Abiertas en alguno de los layers de '-SUP', deben ser Cerradas"
                validaciones2.loc[19,'Cetegoría']='Mejoras'
            else:
                validaciones2.loc[19,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[19,'Observacion']="OK: Se dibujaron polylineas Cerradas en los layers de '-SUP'"
                validaciones2.loc[19,'Cetegoría']='Mejoras'

                #si la polylinea es cerrada sigue validando que tengan el color y grosor bylayer                    
            for mejora in mejoras_poly:
                if mejora.dxf.color == 1 or mejora.dxf.color == 2 or mejora.dxf.color == 3 or mejora.dxf.color == 4 or mejora.dxf.color == 5 or mejora.dxf.color == 32:   
                    band_poly_color_mej.append('0')
                else:
                    band_poly_color_mej.append('-1')

                if mejora.dxf.lineweight==-3:
                    band_poly_gro_mej.append('0')
                else:
                    band_poly_gro_mej.append('-1')

            if '-1' in band_poly_color_mej:
                validaciones2.loc[20,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[20,'Observacion']="Error: Color de polylineas erroneo en los layers de '-SUP' (colores admitidos rojo, amarillo, verde, cian, azul)"
                validaciones2.loc[20,'Cetegoría']='Mejoras'
            
            else:
                validaciones2.loc[20,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[20,'Observacion']="OK: Se dibujaron polylineas Cerradas configuradas correctamente en los layers de '-SUP'"
                validaciones2.loc[20,'Cetegoría']='Mejoras'
                

            if len(mejoras_poly) == (len(forms) + len(forms_empadronados) + len(forms_descubiertos) + len(forms_vacios)):
                validaciones2.loc[21,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[21,'Observacion']="OK: Coinciden la cantidad de polilineas cerradas con la de bloques de formularios"
                validaciones2.loc[21,'Cetegoría']='Mejoras'

            else:
                validaciones2.loc[21,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[21,'Observacion']="ERROR: No Coinciden la cantidad de polilineas cerradas con la de bloques de formularios (form / form_emparonado / form_descubierto)"
                validaciones2.loc[21,'Cetegoría']='Mejoras'
                
                        
            ## INICIO VERIFICACIÓN MEJORA ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.

            
            mejoras_poly= mejoras.query('LWPOLYLINE')
            parcelas_poly= parcelas.query('LWPOLYLINE')
            band_mej_dentro=list() #inicia bandera de control si cada uno de las mejoras estan dentro de una parcela
            for mejora in mejoras_poly: #reccorre poligonos de mejoras
                vertices_e1 = mejora.get_points('xy') #para cada mejora obtiene los vertices y los prepara para la función de control
                vertices_e2 = Vec2.list(vertices_e1)
                band_parc_dentro=list() #bandera que controla si la mejora x esta dentro de alguna de las parcelas
                for parcela in parcelas_poly: #fijado una mejora reccorre poligonos de parcelas para comparar vertices
                    
                    vertices_p1 = list()
                    for vert in parcela.vertices():
                        if vert in vertices_p1:
                            pass
                        else:
                            vertices_p1.append(vert)
                    
                    #vertices_p1 = parcela.get_points('xy')  #para cada parcela obtiene los vertices y los prepara para la función de control
                    vertices_p2 = Vec2.list(vertices_p1)
                    vertices_p3 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=-0.01, closed=True))
                    vertices_p4 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=0.01, closed=True))
                    band_vert_dentro=list() #inicia bandera que valida si los vertices de la mejora caen dentro de el polig. de parcela
                    for i in range (0,len(vertices_e2)): 
                        
                        if ezdxf.math.is_point_in_polygon_2d(vertices_e2[i],vertices_p3,abs_tol=1e-3)==-1: #validación de vertices arroja -1 si cae fuera, 0 si cae en los limites y 1 si cae dentro
                            if ezdxf.math.is_point_in_polygon_2d(vertices_e2[i],vertices_p4,abs_tol=1e-3)==-1:
                                band_vert_dentro.append('-1')
                            else:
                                band_vert_dentro.append('0')
                        else:
                            band_vert_dentro.append('0')
                            
                    if '-1' in band_vert_dentro:
                        band_parc_dentro.append('-1')
                    else:
                        band_parc_dentro.append('0')
                    del band_vert_dentro
                        
                if '0' in band_parc_dentro:
                    band_mej_dentro.append('0')
                    
                else:
                    if mejora.dxf.color ==4 or mejora.dxf.color ==5:
                        band_mej_dentro.append('0') #si la polilinea es cian es porque es balcon, entonces puede caer fuera de la parcela
                    else:
                        band_mej_dentro.append('-1')

                del band_parc_dentro

            if '-1' in band_mej_dentro:
                validaciones2.loc[22,'Resultado']=-1 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[22,'Observacion']="Error: Existe Polígono de superficie fuera de los limites de Parcela"
                validaciones2.loc[22,'Cetegoría']='Mejoras'
            else:
                validaciones2.loc[22,'Resultado']=0 # Valida si las polilineas del layer parcela tienen el grosor y color bylayer
                validaciones2.loc[22,'Observacion']="OK: El ol los polígonos de superficie estan completamente contenidos dentro de la Parcela"
                validaciones2.loc[22,'Cetegoría']='Mejoras'

            ## FIN VERIFICACIÓN MEJORA ESTE COMPLETAMENTE DENTRO DEL POLIGONO DE PARCELA.

    else:

        validaciones2.loc[19,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[19,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"
        validaciones2.loc[19,'Cetegoría']='Mejoras'

        validaciones2.loc[20,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[20,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"        

        validaciones2.loc[21,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[21,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"
        validaciones2.loc[21,'Cetegoría']='Mejoras'

        validaciones2.loc[22,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[22,'Observacion']="OK: No corresponde polig. de superficies puesto que no se han dibujado en los layers '-SUP', verifique que se trate de un CEP Demolición"        


    #--- 2.5.4.1 INICIO Validación de Bloque Formularios--#


    if (len(forms)>0 or len(forms_empadronados)>0):
        
        for form in forms:
            for attrib in form.attribs:
                if attrib.dxf.tag=="Nº_POLIG.":
                    if len(attrib.dxf.text)==0:
                        band_form_polig.append('-1')
                    else:
                        band_form_polig.append('0')
                        if patron_polig.match(attrib.dxf.text):
                            form_polig = (int(attrib.dxf.text))
                            band_letra_form.append('0')
                        else:
                            band_letra_form.append('-1')
                        
                elif attrib.dxf.tag=="TIPO_FORM":
                    if len(attrib.dxf.text)==0:
                        band_T_forms.append('-1')
                    else:
                        band_T_forms.append('0')
                        if patron_polig.match(attrib.dxf.text):
                            form_tipo = (int(attrib.dxf.text))
                            band_letra_form.append('0')
                        else:
                            band_letra_form.append('-1')

                    
                elif attrib.dxf.tag=="Nº_FORM":
                    if len(attrib.dxf.text)==0:
                        band_N_forms.append('-1')
                    else:
                        band_N_forms.append('0')
                        if patron_polig.match(attrib.dxf.text):
                            form_numero = (int(attrib.dxf.text))
                            band_letra_form.append('0')
                        else:
                            band_letra_form.append('-1')
                else:
                    pass
                
        if ("-1" in band_form_polig) or ("-1" in band_T_forms) or ("-1" in band_N_forms):

            validaciones2.loc[23,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones2.loc[23,'Observacion']="Error: En el bloque form no se ha completado algun campo"
            validaciones2.loc[23,'Cetegoría']='Formularios'

        else:
            validaciones2.loc[23,'Resultado']=0 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones2.loc[23,'Observacion']="OK: Se han completado los campos del bloque form"
            validaciones2.loc[23,'Cetegoría']='Formularios'

        if "-1" in band_letra_form:
            validaciones2.loc[24,'Resultado']=-1
            validaciones2.loc[24,'Observacion']="Error: Los campos 'Nº_POLIG.','TIPO_FORM', y 'Nº_FORM' deben completarse unicamente con números enteros"
            validaciones2.loc[24,'Cetegoría']='Mejoras'
        else:
            validaciones2.loc[24,'Resultado']=0
            validaciones2.loc[24,'Observacion']="Ok: Los campos 'Nº_POLIG.','TIPO_FORM', y 'Nº_FORM' se completaron unicamente con números entero"
            validaciones2.loc[24,'Cetegoría']='Mejoras'


        #--- 2.5.4.1 INICIO Validación de Nº de poligono en bloque FOrmularios--#
        if len(forms_polig)>0:

            forms_polig_sorted = sorted(forms_polig)

            if forms_polig_sorted[0] == 1:
                band_1_polig = "0"
            else:
                band_1_polig = "-1"
          
                       
            for i in range (0,len(forms_polig_sorted)):
                if (forms_polig_sorted[i] == (int(forms_polig_sorted[i-1]) + 1)):
                    band_correl_polig.append("0")
                else:
                    band_correl_polig.append("-1")

            band_correl_polig_2 = band_correl_polig.pop(0)


            if band_1_polig == "-1":

                validaciones2.loc[25,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
                validaciones2.loc[25,'Observacion']="Error: El primer Poligono indicado en el bloque form debe ser el Nº '1'"
                validaciones2.loc[25,'Cetegoría']='Formularios'

            else:
                if "-1" in band_correl_polig:
                    validaciones2.loc[25,'Resultado']=-1 # si no hay un -1 en la bandera indica que la validación es correcta.
                    validaciones2.loc[25,'Observacion']="Error: Los poligonos deben numerarse en forma correlativa a partir del Nº '1'"
                    validaciones2.loc[25,'Cetegoría']='Formularios'

                else:
                    validaciones2.loc[25,'Resultado']=0 # si no hay un -1 en la bandera indica que la validación es correcta.
                    validaciones2.loc[25,'Observacion']="OK: Numeros de poligonos en los bloques forms indicados correctamente"
                    validaciones2.loc[25,'Cetegoría']='Formularios'
        else:

            validaciones2.loc[25,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
            validaciones2.loc[25,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
            validaciones2.loc[25,'Cetegoría']='Formularios'

            
    else:
        validaciones2.loc[23,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[23,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
        validaciones2.loc[23,'Cetegoría']='Formularios'


        validaciones2.loc[24,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[24,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
        validaciones2.loc[24,'Cetegoría']='Formularios'

        validaciones2.loc[25,'Resultado']=99 # si no hay un -1 en la bandera indica que la validación es correcta.
        validaciones2.loc[25,'Observacion']="OK: No corresponde validar los formularios dado que no se han insertado bloques para los mismos, verifique que se trate de un baldio"
        validaciones2.loc[25,'Cetegoría']='Formularios'

    #--- 2.5.4.1 FIN Validación de Nº de poligono en bloque FOrmularios--#


    #--- 2.5.5.1 INICIO Validación de restricciones--#

    #--- 2.5.5.1 FIN Validación de restricciones--#

        
#--- 2.5 FIN Validación de elementos del model --#


#--- INICIO Validación Layout-----#

def chequeo_layout():

    global layout
    global layouts
    global parcelas_poly_close
    global cesion_poly_close
    global excedentes_poly_close
    global layers_mejoras_spb
    global car_manz
    global car_parc
    global car_manz_lower
    global car_parc_lower
    global smp
    smp = list()

    patron_layout_cep = ""
    band_pat_layout = list()
    band_muro_frozen = list()
    band_sup_frozen = list()


    #1- INICIO Validar que el layout de la ficha tenga el nombre que debe tener
    patron_layout_cep = re.compile('(^([0-9]{3})-(([0-9]{3})|([0-9]{3}[A-Z]{1}))-(([0-9]{3})|([0-9]{3}[a-z]{1})|(000[A-Z]{1})))$')

    for layout in layouts:

        if (patron_layout_cep.match(layout)):
            smp.append(layout)
        else:
            pass

        band_pat_layout.append(patron_layout_cep.match(layout))


    if all(v is None for v in (band_pat_layout)):
        validaciones2.loc[26,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[26,'Observacion']="Error: El layout de la Ficha catastral no posee el nombre de la nomencltura catastral de la parcela s-m-p(ej: 003-024A-007b)"
        validaciones2.loc[26,'Cetegoría']='Layout'

    else:
        validaciones2.loc[26,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[26,'Observacion']="OK: El Layout de la Ficha catastral posee el nombre SSS-MMMM-PPPP correctamente"
        validaciones2.loc[26,'Cetegoría']='Layout'


    if len(smp)==1:
        
        viewport_smp = (doc.paperspace(f"{smp[0]}")).query("VIEWPORT") #consulta los viewports del layout smp, siempre agrega un elemento primero que creo que corresponde al model, hay que eliminarlo de la lista

        viewport_smp = viewport_smp[1:] #elimina el primer objeto que siempre corresponde al model

        for viewport in viewport_smp:
            if viewport.is_frozen("10-M-MURO-SEPARATIVO-PARC"): #consulta si para el viewport el layer mencionado esta frizado o no
                band_muro_frozen.append("0")
            else:
                band_muro_frozen.append("-1")

            for layer in layers_mejoras_spb:
                if viewport.is_frozen(f"{layer}"):
                    band_sup_frozen.append("0")
                else:
                    band_sup_frozen.append("-1")
               

        if "-1" in band_muro_frozen:
            validaciones2.loc[27,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[27,'Observacion']="Error: El layer 10-M-MURO-SEPARATIVO-PARC no se encuentra frizado en el layout de la ficha catastral"
            validaciones2.loc[27,'Cetegoría']='Layout'

        else:
            validaciones2.loc[27,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[27,'Observacion']="Ok: El layer 10-M-MURO-SEPARATIVO-PARC se encuentra frizado en el layout de la ficha catastral"
            validaciones2.loc[27,'Cetegoría']='Layout'

        if "-1" in band_sup_frozen:
            validaciones2.loc[28,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[28,'Observacion']="Error: Algun layer de Sup. (excluido el de PB) no se encuentra frizado en el layout de la ficha catastral"
            validaciones2.loc[28,'Cetegoría']='Layout'

        else:
            validaciones2.loc[28,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[28,'Observacion']="Ok: Los layers de Sup. (excluido el de PB) se encuentran frizados en el layout de la ficha catastral"
            validaciones2.loc[28,'Cetegoría']='Layout'


        layout_smp = doc.paperspace(f"{smp[0]}")
        lim_lay_smp = layout_smp.get_paper_limits()

        lay_long = abs(lim_lay_smp[1][0] - lim_lay_smp[0][0])
        lay_alt = abs(lim_lay_smp[1][1] - lim_lay_smp[0][1])

        if (abs(lay_long - 0.17)<0.001 and abs(lay_alt - 0.17)<0.001):
            band_limits = 0

        elif (abs(lay_long - 17 ) < 0.1 or abs(lay_alt - 17) < 0.1):
            band_limits = 0

        elif (abs(lay_long - 170) < 1 or abs(lay_alt - 170) < 1):
            band_limits = 0
            
        else:
            band_limits = -1

        if band_limits == -1:
            validaciones2.loc[29,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones2.loc[29,'Observacion']="ERROR: El layout con nombre smp debe medir 17 x 17cm"
            validaciones2.loc[29,'Cetegoría']='Layout'
        else:
            validaciones2.loc[29,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones2.loc[29,'Observacion']="OK: El layout con nombre smp mide 17 x 17cm"
            validaciones2.loc[29,'Cetegoría']='Layout'
    
    else:
            validaciones2.loc[27,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[27,'Observacion']= "Error: No se puden vaidar los layers frizados por existir mas de un layout con el formato sss-mmm-ppp"
            validaciones2.loc[27,'Cetegoría']='Layout'

            validaciones2.loc[28,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[28,'Observacion']="Error: No se puden vaidar los layers frizados por existir mas de un layout con el formato sss-mmm-ppp"
            validaciones2.loc[28,'Cetegoría']='Layout'

            validaciones2.loc[29,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[29,'Observacion']="Error: No se pude validar tamaño de layout por existir mas de un layout con el formato sss-mmm-ppp"
            validaciones2.loc[29,'Cetegoría']='Layout'

   
    #1- FIN Validar que el layout de la ficha tenga el nombre que debe tener
        
    #2- INICIO Validar que el layout tenga la medida que indica las normas


    #5- INICIO validar georreferenciación y comparacion con parcela de catrelsa   
                   
def georref():
    global smp
    global parcelas_poly
    global diferencia_coord
    global diferencia_coord_2
    global diferencia_coord_3
    global diferencia_coord
    global dif_max
    global parc_ant_posgba_2
    global manz_ant_posgba_2

    sm_0=list()
    sm = list()

    parc_ant_posgba = list()
    parc_ant_posgba_2 = list()

    manz_ant_posgba = list()
    manz_ant_posgba_2 = list()
    band_tol_p = list()
    band_tol_m = list()
    parametros = [-0.839549316178051,0.311003700314302,1.0000045988987,-0.000000917727150057199] #parametros de transformación obtenidos para llevar las coordenadas api ciudad3d convertidad a posgar bsas a las coordenadas oficiales de catatsro de las manzanas en posgar bs as
    resp_parc = ""
    resp_manz = ""
    respuesta_parc = ""
    respuesta_manz = ""
    diferencia_coord = list()
    diferencia_coord_2 = list()
    diferencia_coord_3 = list()
    dif_max=0
    parc_ant_posgba_0 = list()
    manz_ant_posgba_0 = list()
    manz_ant_wgs84_0 = list()
    parc_ant_wgs84_0 = list()
    parc_ant_wgs84_1 = list()
    manz_ant_wgs84_1 = list()



    for i in range(len(smp)):
        sm_0=(smp[i].split("-"))
        sm.append(f"{sm_0[0]}-{sm_0[1]}")


    if len(smp)==1:

        validaciones2.loc[30,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[30,'Observacion']="Ok: Existe un unico Layout de Ficha catastral con nomenclatura en su nombre SSS-MMMM-PPPP"
        validaciones2.loc[30,'Cetegoría']='Layout'
   
        try:
            
            resp_parc = get(f"https://epok.buenosaires.gob.ar/catastro/geometria/?smp={smp[0]}") #consulta a la api de ciudad 3d para pedir las coordenadas de la parcela
            resp_manz = get(f"https://epok.buenosaires.gob.ar/catastro/geometria/?sm={sm[0]}") #consulta a la api de ciudad 3d para pedir las coordenadas de la manzana
            respuesta_parc = loads(resp_parc.text)
            respuesta_manz = loads(resp_manz.text)

        except:
                
            validaciones2.loc[31,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[31,'Observacion']="Error: No se puede validar la georref., verifique su conexión, que la parcela se encuentre en Ciudad3d, o la nomenclatura del layout"
            validaciones2.loc[31,'Cetegoría']='Tolerancias'

            validaciones2.loc[32,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones2.loc[32,'Observacion']="Error: No se puede validar la georref., verifique su conexión, que la parcela se encuentre en Ciudad3d, o la nomenclatura del layout"
            validaciones2.loc[32,'Cetegoría']='Tolerancias'

        if len(respuesta_parc)>0 and len(respuesta_manz)>0: #si ciudad 3d responde con coordenadas se hace la validacion
            
            dic_p2=respuesta_parc.get("features") #la respuesta de cudad3d son listas anidadas, se accede hasta la ultima lista con las coordenadas y se guarda en parc_ant_wgs84
            dic_p3= dic_p2[0].get("geometry")
            dic_p4 = dic_p3.get("coordinates")
            dic_p5 = dic_p4[0]
            parc_ant_wgs84_0 = dic_p5[0] ## dic6 es una lista de listas de coordenadas de los vertices de la parcela consultada.

            dic_m2=respuesta_manz.get("features") #la respuesta de cudad3d son listas anidadas, se accede hasta la ultima lista con las coordenadas y se guarda en parc_ant_wgs84
            dic_m3= dic_m2[0].get("geometry")
            dic_m4 = dic_m3.get("coordinates")
            dic_m5 = dic_m4[0]
            manz_ant_wgs84_0 = dic_m5[0] ## dic6 es una lista de listas de coordenadas de los vertices de la parcela consultada.

            for m in manz_ant_wgs84_0:
                
                manz_ant_wgs84_1.append(GeoSeries(geometry.Point(m[0],m[1]),crs="EPSG:4326",))
            for p in parc_ant_wgs84_0:
            
                parc_ant_wgs84_1.append(GeoSeries(geometry.Point(p[0],p[1]),crs="EPSG:4326",))

            for m in manz_ant_wgs84_1:
                manz_ant_posgba_0.append(m.to_crs(9498))

            for p in parc_ant_wgs84_1:
                parc_ant_posgba_0.append(p.to_crs(9498))

            z = list()
            for m in manz_ant_posgba_0:
                x = (m.x)
                y = (m.y)
                z.append(x)
                z.append(y)
                manz_ant_posgba.append(z)
                z = list()

            z = list()
            for p in parc_ant_posgba_0:
                x = (p.x)
                y = (p.y)
                z.append(x)
                z.append(y)
                parc_ant_posgba.append(z)
                z = list()   

            for i in range (len(parc_ant_posgba)): # se aplica los parametros de transfoormación para la parcela antecedente de ciudad3d asi cae correstamente con las coordenadas de catastro y se guarda en parc_ant_posgba_2
                a = parc_ant_posgba[i]
                c_correg = list()
                a_correg = parametros[0]+(parametros[2]*a[0])-(parametros[3]*a[1])
                b_correg = parametros[1]+(parametros[2]*a[1])-(parametros[3]*a[0])
                c_correg.append(a_correg)
                c_correg.append(b_correg)
                parc_ant_posgba_2.append(c_correg)
 
            for i in range (len(manz_ant_posgba)): # se aplica los parametros de transfoormación para la parcela antecedente de ciudad3d asi cae correstamente con las coordenadas de catastro y se guarda en parc_ant_posgba_2
            
                a = manz_ant_posgba[i]
                c_correg = list()
                a_correg = parametros[0]+(parametros[2]*a[0])-(parametros[3]*a[1])
                b_correg = parametros[1]+(parametros[2]*a[1])-(parametros[3]*a[0])
                c_correg.append(a_correg)
                c_correg.append(b_correg)
                manz_ant_posgba_2.append(c_correg)

            if len(parcelas_poly):
            
                ver_cep_p1 = parcelas_poly[0].get_points('xy')  #para cada parcela obtiene los vertices y los prepara para la función de control
                ver_cep_p2 = Vec2.list(ver_cep_p1) #arma el vector necesariopara la funcion que verifica que cada vertice este dentro del poligono

                ver_ant_p1 = parc_ant_posgba_2 #prepara la parcela antecedente transformada para compararla con la medida
                ver_ant_p2 = Vec2.list(ver_ant_p1)
                ver_ant_p3 = list(ezdxf.math.offset_vertices_2d(ver_ant_p2,offset=0.51, closed=True)) #arma ofsets de 0,5m para afuera y para adentro de la parcela antecedente y la parcela medida debe caer dentro de esos dos poligonos
                ver_ant_p4 = list(ezdxf.math.offset_vertices_2d(ver_ant_p2,offset=-0.51, closed=True))

                ver_ant_m1 = manz_ant_posgba_2 #prepara la parcela antecedente transformada para compararla con la medida
                ver_ant_m2 = Vec2.list(ver_ant_m1)
                ver_ant_m3 = list(ezdxf.math.offset_vertices_2d(ver_ant_m2,offset=0.51, closed=True)) #arma ofsets de 0,5m para afuera y para adentro de la parcela antecedente y la parcela medida debe caer dentro de esos dos poligonos
                
                for vert in ver_cep_p2:
                    if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p3,abs_tol=1e-4)==-1: #si esta validacion da -1 quiere decir que la parcela del cep es mas grande que la antecedente con una tolerancia de 51cm
                        band_tol_p.append("-1")   #valida que la parcela caiga dentro del ofset mayor de 0,5m de la parcela antecedente

                    else:
                        if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_p4,abs_tol=1e-4)==-1:
                            band_tol_p.append("0") #valida que la parcela caiga fuera del ofset menor de 0,5m de la parcela antecedente

                        else:
                            band_tol_p.append("-2")

                    if ezdxf.math.is_point_in_polygon_2d(vert,ver_ant_m3,abs_tol=1e-4)==-1: #si esta validacion da -1 quiere decir que la parcela del cep es mas grande que la antecedente con una tolerancia de 51cm
                        band_tol_m.append("-1")   #valida que la parcela caiga dentro del ofset mayor de 0,5m de la manzana antecedente

                    else:
                        band_tol_m.append("0")

                for vert in ver_cep_p1:

                    diferencia_coord = list()

                    for vert1 in ver_ant_p1:
                      
                        diferencia_coord.append(math.sqrt(((vert[0]-vert1[0])**2)+((vert[1]-vert1[1])**2)))

                    diferencia_coord_2.append(min(diferencia_coord))
                    
                diferencia_coord_3 = sorted(diferencia_coord_2, reverse = False)

                dif_max = round(max(diferencia_coord_3),2)
                
                if "-1" in band_tol_m:
                    validaciones2.loc[31,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                    validaciones2.loc[31,'Observacion']="Error: La parcela medida no se ha georreferenciado correctamente"
                    validaciones2.loc[31,'Cetegoría']='Tolerancias'

                    validaciones2.loc[32,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                    validaciones2.loc[32,'Observacion']="Error: La parcela medida no se ha georreferenciado correctamente"
                    validaciones2.loc[32,'Cetegoría']='Tolerancias'

                else:
                    validaciones2.loc[31,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                    validaciones2.loc[31,'Observacion']="Ok: La parcela medida se encuentradentro de la manzana a la cual pertenece"
                    validaciones2.loc[31,'Cetegoría']='Tolerancias'

                        
                    if "-1" in band_tol_p:
                        
                        validaciones2.loc[32,'Resultado']=50 # si hay un -1 en la bandera arroja error 
                        validaciones2.loc[32,'Observacion']="Verificar: La parcela medida excede la tolerancia admitida respecto a la parcela antecedente o no se ha georreferenciado correctamente"
                        validaciones2.loc[32,'Cetegoría']='Tolerancias'

                    elif "-2" in band_tol_p:
                        
                        validaciones2.loc[32,'Resultado']=50 # si hay un -1 en la bandera arroja error 
                        validaciones2.loc[32,'Observacion']="Verificar: La parcela medida excede la tolerancia admitida respecto a la parcela antecedente o no se ha georreferenciado correctamente"
                        validaciones2.loc[32,'Cetegoría']='Tolerancias'
                        
                    else:

                        if dif_max >= 1.00:
                                validaciones2.loc[32,'Resultado']=50 # si hay un -1 en la bandera arroja error 
                                validaciones2.loc[32,'Observacion']="Error: La parcela medida excede la tolerancia admitida respecto a la parcela de Ciudad 3d"
                                validaciones2.loc[32,'Cetegoría']='Tolerancias'
                        else:

                            if dif_max > 0.50:
                                
                                validaciones2.loc[32,'Resultado']=50 # si hay un -1 en la bandera arroja error 
                                validaciones2.loc[32,'Observacion']="Verificar: Existe diferencias con parcela de Ciudad 3d, Verificar cumplimiento de tolerancias con ficha parcelaria"
                                validaciones2.loc[32,'Cetegoría']='Tolerancias'

                            else:
                                
                                validaciones2.loc[32,'Resultado']=0 # si hay un -1 en la bandera arroja error 
                                validaciones2.loc[32,'Observacion']="Ok: La parcela medida se encuentra en tolerancia con respeto a la parcela antecedente"
                                validaciones2.loc[32,'Cetegoría']='Tolerancias'
            else:
                validaciones2.loc[31,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[31,'Observacion']="Error: No se puede validar la georreferenciación porque no se encuentra dubujada la parcela como polilinea cerrada en el layer 09-M-PARCELA"
                validaciones2.loc[31,'Cetegoría']='Tolerancias'

                validaciones2.loc[32,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[32,'Observacion']="Error: No se puede validar la georreferenciación porque no se encuentra dubujada la parcela como polilinea cerrada en el layer 09-M-PARCELA"
                validaciones2.loc[32,'Cetegoría']='Tolerancias'
        else:

                validaciones2.loc[31,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[31,'Observacion']="Error: No puede validarse la georref., no se encuentra en Ciudad3d la parcela indicada en el layout o no se puede conectarse con Ciudad3d"
                validaciones2.loc[31,'Cetegoría']='Tolerancias'

                validaciones2.loc[32,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
                validaciones2.loc[32,'Observacion']="Error: No puede validarse la georref., no se encuentra en Ciudad3d la parcela indicada en el layout o no se puede conectarse con Ciudad3d"
                validaciones2.loc[32,'Cetegoría']='Tolerancias'
   
    
    elif len(smp)>1:
        validaciones2.loc[30,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[30,'Observacion']="Error: Existen mas de un Layout de Ficha catastral con nomenclatura en su nombre SSS-MMMM-PPPP"
        validaciones2.loc[30,'Cetegoría']='Layout'

        validaciones2.loc[31,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[31,'Observacion']="Error: Existen más de un Layout con nombre SSS-MMMM-PPPP, con lo que no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones2.loc[31,'Cetegoría']='Layout'

        validaciones2.loc[32,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[32,'Observacion']="Error: Existen más de un Layout con nombre SSS-MMMM-PPPP, con lo que no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones2.loc[32,'Cetegoría']='Layout'

    else:

        validaciones2.loc[30,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[30,'Observacion']="Error: No existe layout cuyo nombre tenga formato de nomenclatura catastral SSS-MMMM-PPPP"
        validaciones2.loc[30,'Cetegoría']='Layout'

        validaciones2.loc[31,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[31,'Observacion']="Error: No existe layout cuyo nombre tenga formato ‘SSS-MMMM-PPPP’, no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones2.loc[31,'Cetegoría']='Layout'

        validaciones2.loc[32,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones2.loc[32,'Observacion']="Error: No existe layout cuyo nombre tenga formato ‘SSS-MMMM-PPPP’, no es posible validar las diferencias entre parcela medida y antecedente"
        validaciones2.loc[32,'Cetegoría']='Layout'
        

def resumen():
    global mejoras_poly
    global parcelas_poly
    global lados_parcelas_l
    global excedentes_poly
    global dif_max
    global forms
    global forms_empadronados
    global forms_descubiertos
    global validaciones2
    global validaciones
    global layers_mejoras
    global pages_IFTAM_text
    global pages_IFFVN_text
    global pages_IFDOM_text
    global piso_con_mejoras
    global info_form_emp
    global info_form_nuevo
    global agip_supnueva
    global supdemo_3
    global comparacion
    global restricciones
    global particularidades
    global notas
    global cont_3
    global notas_0
    global notas_1
    global notas_2
    global band_notas

    global dif_agip

    global area_parc_dxf
    global area_excedente_dxf
    global plantas_dxf
    global cubierta_dxf
    global semicubierta_dxf
    global descubierta_dxf
    global sup_emp_dxf
    global sup_nueva_dxf
    
    global deslinde
    global medidas

    global sup_cub_dxf
    global sup_semicub_dxf
    global sup_descub_dxf
    global sup_descont_dxf

    global band_mejora_cub_arc_0
    global band_mejora_semi_arc_0
    global band_mejora_desc_arc_0
    global band_mejora_emp_arc_0
    global band_mejora_nueva_arc_0

    formul_0 = list()
    info_form_nuevo_1 = list()
    notas_2 = list()
    band_notas = list()

    cubierta_dxf = round(sum(sup_cub_dxf),2)
    semicubierta_dxf = round(sum(sup_semicub_dxf),2)
    descubierta_dxf = round(sum(sup_descub_dxf),2)
    
    sup_emp_dxf = 0
    sup_nueva_dxf = 0
    band_2 = list()
    band_agip_dxf = list()
    band_medida = list()

    #calcular superficie de parcela, sup excedente, sup total construida, sup no empadronada, sup empadronada.
    
    if len(parcelas_poly):
        area_parc_dxf = round(ezdxf.math.area(Vec2.list(parcelas_poly[0].get_points('xy'))),2)
    else:
        area_parc_dxf = 0
 

    if len(excedentes_poly):
        #hacer lo mismo que con las construcciones
      area_excedente_dxf = round(ezdxf.math.area(Vec2.list(excedentes_poly[0].get_points('xy'))),2)
    else:
        area_excedente_dxf = round(0,2)

    for i in range (len(info_form_emp)): #calcula la superficie empadronada del archivo dxf
        sup_emp_dxf = sup_emp_dxf + info_form_emp[i]
    
    sup_emp_dxf = round(sup_emp_dxf,2)


    for i in range (len(info_form_nuevo)):
       formul_0.append((info_form_nuevo[i])['form'])

    formul = list(set(formul_0))

    for i in formul:

        lista = [indice for indice, dato in enumerate(info_form_nuevo) if dato['form'] == i]
        poligonos = ""
        sumar_sup = 0
        for k in range (len(lista)):
            poligonos = poligonos + "," + (info_form_nuevo[k])["polig"] #comprimir poligonos de los k
            sumar_sup = sumar_sup + float((info_form_nuevo[k])["sup"])

        poligonos = poligonos[1:]
        info_form_nuevo_1.append({"form":i,"polig":f"{poligonos}","sup":sumar_sup}) #comprime todas las superficies de un mismo formulario en un unico campo
        
        for i in range(len(info_form_nuevo_1)):
            sup_nueva_dxf = sup_nueva_dxf + info_form_nuevo_1[i]["sup"]

        sup_nueva_dxf = round(sup_nueva_dxf,2)

    plantas_dxf = len(piso_con_mejoras)

    #generar una lista de diccionarios en la cual este comprimida la suma de las superficies que corresponden al mismo formulario
        
    if len(pages_IFTAM_text)>0 and len(pages_IFFVN_text)>0 and len(pages_IFDOM_text)>0:
        analisis_IFTAM()
        analisis_IFFVN()
        analisis_IFDOM()

        #variables del form de mensura
        global cubierta_3
        global mensura_3
        global plantas_3
        global semi_3
        global des_3

        global cur_afectaciones
        global zonificacion
        global aph

        #variables del form de agip
        global agip_supnueva
        global agip_polig
        global agip_destinos
        global agip_supexis
        global agip_fechaconst

        #variables del form de dominio
        global sup_tit

        dif_mensura_dxf = area_parc_dxf - mensura_3
        dif_plantas_dxf = plantas_dxf - plantas_3

        sup_cub_dxf_0 = cubierta_dxf
        sup_semicub_dxf_0 = semicubierta_dxf 
        sup_descub_dxf_0 = descubierta_dxf
        
        dif_cubierta_dxf = round(sup_cub_dxf_0,0) - round(cubierta_3,0)
        dif_semi_dxf = round(sup_semicub_dxf_0,0) - round(semi_3,0)
        dif_desc_dxf  = round(sup_descub_dxf_0,0) - round(des_3,0)
        
        notas_df = read_excel('notas.xls')

        notas_comparar = dict(zip(notas_df.iloc[:, 0], notas_df.iloc[:, 1]))

        caracteres_eliminar = [",",".",";"]


        for nota in notas_1:
            for char in caracteres_eliminar:
                notas_2.append(nota.replace(char, "")) #elimina ".", "," y ";" de las notas cargadas por el prof y las guarda nota por nota en una lista

        for nota in notas_2:
            words1 = nota.split()
            for clave, valor in notas_comparar.items():
                words2 = valor.split()
                seq = difflib.SequenceMatcher(None, words1, words2)
                similarity = seq.ratio()
                if similarity >0.5:
                    band_notas.append(clave)
                else:
                    pass
                del words2
            del words1

        if abs(dif_mensura_dxf) > 0.01:
            validaciones2.loc[33,'Resultado']=-1
            validaciones2.loc[33,'Observacion']="Error: No coincide la Superficie de la Parcela en el dxf con la declarada en el formulario de Mensura"
        else:
            validaciones2.loc[33,'Resultado']=0
            validaciones2.loc[33,'Observacion']="Ok: Coinciden la Superficie de la Parcela en el dxf con la declarada en el formulario de Mensura"

        if dif_plantas_dxf != 0:
            validaciones2.loc[34,'Resultado']=-1
            validaciones2.loc[34,'Observacion']="Error: No coincide la N° de Plantas en las que se dibujó en el dxf con el N° de plantas declaradas en el form de mensura"
        else:
            validaciones2.loc[34,'Resultado']=0
            validaciones2.loc[34,'Observacion']="Ok: Coincide la N° de Plantas en las que se dibujó en el dxf con el N° de plantas declaradas en el form de mensura"

        if abs(dif_cubierta_dxf) > 0.01 and len(band_mejora_cub_arc_0)==0:
            validaciones2.loc[35,'Resultado']=-1
            validaciones2.loc[35,'Observacion']="Error: No coincide la Sup. Cubierta dibujada en el dxf con la superficie cubierta declarada en el form de mensura"
        
        elif abs(dif_cubierta_dxf) > 0.01 and len(band_mejora_cub_arc_0)!=0:
            validaciones2.loc[35,'Resultado']=50
            validaciones2.loc[35,'Observacion']="Verificar: Algun poligono cubierto o poligono interno posee un lado de arco, verificar sup. cubierta de formularios y dxf manualmente"
        else:
            validaciones2.loc[35,'Resultado']=0
            validaciones2.loc[35,'Observacion']="Ok:Coincide la Sup. Cubierta dibujada en el dxf con la superficie cubierta declarada en el form de mensura"

        if abs(dif_semi_dxf) > 0.01 and len(band_mejora_semi_arc_0)==0:
            validaciones2.loc[36,'Resultado']=-1
            validaciones2.loc[36,'Observacion']="Error: No coincide la Sup. semicubierta dibujada en el dxf con la superficie semicubierta declarada en el form de mensura"
        
        elif abs(dif_semi_dxf) > 0.01 and len(band_mejora_semi_arc_0)!=0:
            validaciones2.loc[36,'Resultado']=50
            validaciones2.loc[36,'Observacion']="Verificar: Algun poligono semicub o poligono interno posee un lado de arco, verificar sup. cubierta de formularios y dxf manualmente"
        
        else:
            validaciones2.loc[36,'Resultado']=0
            validaciones2.loc[36,'Observacion']="Ok: Coincide la Sup. Semicubierta dibujada en el dxf con la superficie semicubierta declarada en el form de mensura"

        if abs(dif_desc_dxf) > 0.01 and len(band_mejora_desc_arc_0)==0:
            validaciones2.loc[37,'Resultado']=-1
            validaciones2.loc[37,'Observacion']="Error: No coincide la Sup. descubierta dibujada en el dxf con la superficie descubierta declarada en el form de mensura"
        
        elif abs(dif_desc_dxf) > 0.01 and len(band_mejora_desc_arc_0)!=0:
            validaciones2.loc[37,'Resultado']=50
            validaciones2.loc[37,'Observacion']="Verificar: Algun poligono descub o poligono interno posee un lado de arco, verificar sup. cubierta de formularios y dxf manualmente"
        
        else:
            validaciones2.loc[37,'Resultado']=0
            validaciones2.loc[37,'Observacion']="Ok: Coincide la Sup. descubierta dibujada en el dxf con la superficie descubierta declarada en el form de mensura"

        #Calcula cantidad de lados de la parcela, medidas de cada lado y contrastarlo con las medidas y cantidad de lados indicadas en el formulario de mensura
        if lados_parcelas_l[0] == len(medidas):
            validaciones2.loc[38,'Resultado']=0
            validaciones2.loc[38,'Observacion']="Ok: Coincide la cantidad de lados de la parcela del dxf con la cantidad de rumbos declarados en el form. de mensura"

            for medida in medidas:
                if medida in medidas_dxf:
                    band_medida.append('0')
                else:
                    band_medida.append('-1')
            
            if "-1" in band_medida:
                validaciones2.loc[39,'Resultado']=-1
                validaciones2.loc[39,'Observacion']="Error: No coinciden las medida de lados declaradas en el form de mensura con las medidas de los lados de la parcela del dxf"
            else:
                validaciones2.loc[39,'Resultado']=0
                validaciones2.loc[39,'Observacion']="Ok: Coinciden las medida de lados declaradas en el form de mensura con las medidas de los lados de la parcela del dxf"
            
        else:
            validaciones2.loc[38,'Resultado']=-1
            validaciones2.loc[38,'Observacion']="Error: No coincide la cantidad de lados de la parcela del dxf con la cantidad de rumbos declarados en el form. de mensura"

            validaciones2.loc[39,'Resultado']=-1
            validaciones2.loc[39,'Observacion']="Error: No coincide la cantidad de lados de la parcela del dxf con la cantidad de rumbos declarados en el form. de mensura"

        if cont_3 > 0:

            if ("contravencion" in band_notas):
                validaciones2.loc[40,'Resultado']=0
                validaciones2.loc[40,'Observacion']="Ok: Se detectó nota de Superficie en contravención de los RT en el Campo 'Notas' del Form. de Mensura"
            else:
                validaciones2.loc[40,'Resultado']=-1
                validaciones2.loc[40,'Observacion']="Error: No se detectó nota de Superficie en contravención de los RT en el Campo 'Notas' del Form. de Mensura"
        else:
            validaciones2.loc[40,'Resultado']=99
            validaciones2.loc[40,'Observacion']="Ok: No corresponde validar nota de Superficie en contravención por no haberse declarado la misma"

        if (mensura_3 - sup_tit) >0:
            if (mensura_3 - sup_tit) > (0.05 * mensura_3):

                if ("excedente_1" in band_notas) or ("excedente_2" in band_notas):
                    validaciones2.loc[41,'Resultado']=0
                    validaciones2.loc[41,'Observacion']="Ok: Se ha detectado alguna de las notas de Excedente de los RT en el campo 'Notas' del formulario tecnico de Mensura"
                else:
                    validaciones2.loc[41,'Resultado']=-1
                    validaciones2.loc[41,'Observacion']="Error: No se ha detectado alguna de las notas de Excedente de los RT en el campo 'Notas' del formulario tecnico de Mensura"
            else:
                validaciones2.loc[41,'Resultado']=99
                validaciones2.loc[41,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"

        elif (mensura_3 - sup_tit) == 0:
            validaciones2.loc[41,'Resultado']=99
            validaciones2.loc[41,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"

        elif ((mensura_3 - sup_tit) < 0):

            if (abs((mensura_3 - sup_tit)) > (0.05 * mensura_3)):
                validaciones2.loc[41,'Resultado']=50
                validaciones2.loc[41,'Observacion']="Verificar: Sup. s/título de form de dominio es mayor a sup en form de mensura (mayor al 5%) verifique que sup. s/titulo se declaró correctamente"

            else:
                validaciones2.loc[41,'Resultado']=99
                validaciones2.loc[41,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"
        
        else:
            validaciones2.loc[41,'Resultado']=99
            validaciones2.loc[41,'Observacion']="Ok: No corresponde validar campo 'Notas' y 'Particularidades' de excedente"
            
        if "excedente" in (particularidades[0].lower().replace(" ","")):

            if "excedente_2" in band_notas:
                validaciones2.loc[42,'Resultado']=0
                validaciones2.loc[42,'Observacion']="Ok: En particularidades se declaró excedente y se indico nota del mismo en el campo 'Notas' del form. tecnico de Mensura"
            else:
                validaciones2.loc[42,'Resultado']=0
                validaciones2.loc[42,'Observacion']="Error: En particularidades se declaró excedente y no se indico nota del mismo en el campo 'Notas' del form. tecnico de Mensura"
        else:
            validaciones2.loc[42,'Resultado']=99
            validaciones2.loc[42,'Observacion']="Ok: En particularidades no se declaró excedente, no corresponde validar nota de excedente en form. técnico de Mensura"

        if dif_agip =="no":

            if "agip_nodif" in band_notas:
                validaciones2.loc[43,'Resultado']=0
                validaciones2.loc[43,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
                
                validaciones2.loc[44,'Resultado']=0
                validaciones2.loc[44,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
            
            else:
                if "cep_demolicion" in band_notas:
                    validaciones2.loc[43,'Resultado']=0
                    validaciones2.loc[43,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota de Cep demolicion en el campo notas del form. tecnico de mensura"

                    validaciones2.loc[44,'Resultado']=0
                    validaciones2.loc[44,'Observacion']="Ok: se declaró que no difiere con agip y se detectó la nota de Cep demolicion en el campo notas del form. tecnico de mensura"
                else:
                    validaciones2.loc[43,'Resultado']=-1
                    validaciones2.loc[43,'Observacion']="Error: se declaró que no difiere con agip y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"

                    validaciones2.loc[44,'Resultado']=-1
                    validaciones2.loc[44,'Observacion']="Error: se declaró que no difiere con agip y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
        elif dif_agip =="si":

            if supdemo_3>0:
                if "agip_dif_menos" in band_notas:
                    validaciones2.loc[43,'Resultado']=0
                    validaciones2.loc[43,'Observacion']="Ok: se declaró que difiere con agip, superficie demolida y se detectó la nota correspondiente en el campo notas del form. tecnico de mensura"
                else:
                    validaciones2.loc[43,'Resultado']=-1
                    validaciones2.loc[43,'Observacion']="Error: se declaró que difiere con agip, superficie demolida y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
            else:
                validaciones2.loc[43,'Resultado']=99
                validaciones2.loc[43,'Observacion']="Ok: No corresponde validar nota de demolicion por no haberse declarado la misma en el form resumen"


            if len(agip_supnueva)>0:

                if sum(agip_supnueva)>0:
                    if "agip_dif_mas" in band_notas:
                        validaciones2.loc[44,'Resultado']=0
                        validaciones2.loc[44,'Observacion']="Ok: se declaró que difiere con agip, superficie nueva y se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
                    else:
                        validaciones2.loc[44,'Resultado']=-1
                        validaciones2.loc[44,'Observacion']="Error: se declaró que difiere con agip, superficie nueva y no se detectó la nota correspondiente segun los RT en el campo notas del form. tecnico de mensura"
                else:
                    validaciones2.loc[44,'Resultado']=99
                    validaciones2.loc[44,'Observacion']="Ok: No corresponde validar nota de superficie a empadronar por no haberse declarado superficie nueva en el from resumen"

            else:
                validaciones2.loc[44,'Resultado']=-1
                validaciones2.loc[44,'Observacion']="Error: se declaró que difiere con agip, y no se indicó ningun valor en el campo sup. nueva en el form. resumen"  
      
        else:
            validaciones2.loc[43,'Resultado']=-1
            validaciones2.loc[43,'Observacion']="Error: no se puede validar nota de agip por no haberse completado si difere o no con agip las construcciones relevadas"
            
            validaciones2.loc[44,'Resultado']=-1
            validaciones2.loc[44,'Observacion']="Error: no se puede validar nota de agip por no haberse completado si difere o no con agip las construcciones relevadas"
        
        if "-1" in band_cur_parcela:
            validaciones2.loc[45,'Resultado']=-1
            validaciones2.loc[45,'Observacion']="Error: No se puede comprobar APH y afectaciones de la parcela por no poder conectarse con Ciudad 3d, verifique conexión de internet"
        else:
            if "cep_demolicion" in band_notas:
                if aph != "No":
                    validaciones2.loc[45,'Resultado']=-1
                    validaciones2.loc[45,'Observacion']="Error: Se ha declarado CEP Demolición y la parcela esta afectada a APH"

                else:
                    validaciones2.loc[45,'Resultado']=0
                    validaciones2.loc[45,'Observacion']="Ok: Se ha declarado CEP Demolición y la parcela no esta afectada a APH"

            else:
                validaciones2.loc[45,'Resultado']=0
                validaciones2.loc[45,'Observacion']="Ok: No se ha declarado CEP Demolición"


            if aph != "No":
                if "aph" in band_notas:
                    validaciones2.loc[46,'Resultado']=0
                    validaciones2.loc[46,'Observacion']="Ok: Se ha indicado la Nota de Aph en formulario de Mensura"
                else:
                    validaciones2.loc[46,'Resultado']=-1
                    validaciones2.loc[46,'Observacion']="Error: No se ha indicado la Nota de Aph en formulario de Mensura y la parcela se encuentra catalogada"
            else:
                validaciones2.loc[46,'Resultado']=99
                validaciones2.loc[46,'Observacion']="Ok: No corresponde validar nota de Aph"
            
            if "Cinturon Digital" in cur_afectaciones:
                if "Cinturon Digital" in particularidades:
                    if "Cinturon Digital".lower().replace(" ","") in (notas_0[0].lower()):
                        validaciones2.loc[47,'Resultado']=0
                        validaciones2.loc[47,'Observacion']="Ok: Se indicó nota de 'Afectación a Cinturon Digital' en Notas del formulario de Mensura"
                    else:
                        validaciones2.loc[47,'Resultado']=-1
                        validaciones2.loc[47,'Observacion']="Error: No se indicó nota de 'Afectación a Cinturon Digital' en Notas del formulario de Mensura"
                else:
                    validaciones2.loc[47,'Resultado']=-1
                    validaciones2.loc[47,'Observacion']="Error: No se indicó nota de 'Afectación a Cinturon Digital' en Particularidades del formulario de Mensura"
            else:
                validaciones2.loc[47,'Resultado']=99
                validaciones2.loc[47,'Observacion']="Ok: No corresponde validar nota de 'Afectación Cinturon Digital'"

            if "Afectación por Apertura" in cur_afectaciones:
                if "Afectación por Apertura" in particularidades:
                    if "Afectación por Apertura".lower().replace(" ","") in (notas_0[0].lower()):
                        validaciones2.loc[48,'Resultado']=0
                        validaciones2.loc[48,'Observacion']="Ok: Se indicó nota de 'Afectación por Apertura' en Notas del formulario de Mensura"
                    else:
                        validaciones2.loc[48,'Resultado']=-1
                        validaciones2.loc[48,'Observacion']="Error: No se indicó nota de 'Afectación por Apertura' en Notas del formulario de Mensura"
                else:
                    validaciones2.loc[48,'Resultado']=-1
                    validaciones2.loc[48,'Observacion']="Error: No se indicó nota de 'Afectación por Apertura' en Particularidades del formulario de Mensura"
            else:
                validaciones2.loc[48,'Resultado']=99
                validaciones2.loc[48,'Observacion']="Ok: No corresponde validar nota 'Afectación por Apertura'"

            if "Afectación por Ensanche" in cur_afectaciones:
                if "Afectación por Ensanche" in particularidades:
                    if "Afectación por Ensanche".lower().replace(" ","") in (notas_0[0].lower()):
                        validaciones2.loc[49,'Resultado']=0
                        validaciones2.loc[49,'Observacion']="Ok: Se indicó nota de 'Afectación por Ensanche' en Notas del formulario de Mensura"
                    else:
                        validaciones2.loc[49,'Resultado']=-1
                        validaciones2.loc[49,'Observacion']="Error: No se indicó nota de 'Afectación por Ensanche' en Notas del formulario de Mensura"
                else:
                    validaciones2.loc[49,'Resultado']=-1
                    validaciones2.loc[49,'Observacion']="Error: No se indicó nota de 'Afectación por Ensanche' en Particularidades del formulario de Mensura"
            else:
                validaciones2.loc[49,'Resultado']=99
                validaciones2.loc[49,'Observacion']="Ok: No corresponde validar nota 'Afectación por Ensanche'"

            if "Linea de Edificacion Particularizada" in cur_afectaciones:
                if "Linea de Edificacion Particularizada" in particularidades:
                    if "Linea de Edificacion Particularizada".lower().replace(" ","") in (notas_0[0].lower()):
                        validaciones2.loc[50,'Resultado']=0
                        validaciones2.loc[50,'Observacion']="Ok: Se indicó nota de 'Afectación por Linea de Edificacion Particularizada' en Notas del formulario de Mensura"
                    else:
                        validaciones2.loc[50,'Resultado']=-1
                        validaciones2.loc[50,'Observacion']="Error: No se indicó nota de 'Afectación por Linea de Edificacion Particularizada' en Notas del formulario de Mensura"
                else:
                    validaciones2.loc[50,'Resultado']=-1
                    validaciones2.loc[50,'Observacion']="Error: No se indicó nota de 'Afectación por Linea de Edificacion Particularizada' en Particularidades del formulario de Mensura"
            else:
                validaciones2.loc[50,'Resultado']=99
                validaciones2.loc[50,'Observacion']="Ok: No corresponde validar nota 'Afectación por Linea de Edificacion Particularizada'"       

    else:
        validaciones2.loc[33,'Resultado']=-1
        validaciones2.loc[33,'Observacion']="Error: No es posible validar los formularios por no haberse cargado los mismos"

def mostrar_resumen():
    global area_parc_dxf
    global area_excedente_dxf
    global plantas_dxf
    global cubierta_dxf
    global semicubierta_dxf
    global descubierta_dxf
    global sup_emp_dxf
    global sup_nueva_dxf
    global smp

    if len(smp)==1:
        nom_parc=smp[0]
    else:
        nom_parc= "Error"

    print(messagebox.showinfo(title="Resumen Archivo DXF",message=f"SMP: {nom_parc}\nSup. Parc: {area_parc_dxf}\n\nSup. excedente: {area_excedente_dxf}\n\nN° de Plantas: {plantas_dxf}\n\nSup. Cubierta:{cubierta_dxf}\nSup semicub.: {semicubierta_dxf}\nSup. Descub: {descubierta_dxf}\n\nSup. Empadronada: {sup_emp_dxf}\nSup. A empadronar: {sup_nueva_dxf}"))

    
        
def descargar_dxf():          
    global parc_ant_posgba_2
    global manz_ant_posgba_2
    global parc_ant_posgba_4
    global manz_ant_posgba_4
    global parcelas_poly
    global last_dir
    
    manz_ant_posgba_4 = list()
    parc_ant_posgba_4 = list()

    doc2 = ezdxf.new("AC1018")
    mdl2 = doc2.modelspace()
    parc_ant_lay = doc2.layers.add("Parcela_Ciudad_3D")
    manz_ant_lay = doc2.layers.add("Manzana_Ciudad_3D")
    parc_cep_lay = doc2.layers.add("Parcela_Medida")
    parc_ant_lay.color = 1
    manz_ant_lay.color = 4
    parc_cep_lay.color = 5

    if len(parcelas_poly)==1:
        points_parc_cep = parcelas_poly[0].get_points('xy')
        parc_cep = mdl2.add_lwpolyline(points_parc_cep)
        parc_cep.dxf.layer = "Parcela_Medida"
        parc_cep.closed = True

    else:
        pass
    if len(manz_ant_posgba_2):
        for vert in  manz_ant_posgba_2:
            c=list()
            a = vert[0].tolist()
            b = vert[1].tolist()
            c.append(a[0])
            c.append(b[0])
            manz_ant_posgba_4.append(c)

        points_manz_ant = manz_ant_posgba_4 
        manz_ant = mdl2.add_lwpolyline(points_manz_ant)
        manz_ant.dxf.layer = "Manzana_Ciudad_3D"
        manz_ant.closed = True

    else:
        pass

    if len(parc_ant_posgba_2):

        for vert in  parc_ant_posgba_2:
            c=list()
            a = vert[0].tolist()
            b = vert[1].tolist()
            c.append(a[0])
            c.append(b[0])
            parc_ant_posgba_4.append(c)
            
        points_parc_ant = parc_ant_posgba_4 
        parc_ant=mdl2.add_lwpolyline(points_parc_ant)
        parc_ant.dxf.layer = "Parcela_Ciudad_3D"
        parc_ant.closed = True

    else:
        pass
    
    if last_dir!= "":
        doc2.saveas(filedialog.asksaveasfilename(title="guardar", initialdir=f"{last_dir}", initialfile="Comparacion.dxf", filetypes = [("Drawing Exchange Format", "*.dxf")]))
    else:
        doc2.saveas(filedialog.asksaveasfilename(title="guardar", initialdir="C:/", initialfile="Comparacion.dxf", filetypes = [("Drawing Exchange Format", "*.dxf")]))

            

    #5- FIN validar que los viewports de los layouts esten en la misma
    #escala que la declarada


#--- FIN Validación Layout-----#
#INICIO CONSULTA CUR PARCELA

def cur_parcela():
    global resp_parc_datos_0
    global resp_parc_datos
    global smp
    global band_cur_parcela
    global cur_afectaciones
    global zonificacion
    global aph
    band_cur_parcela = list()
    zonificacion = list()
    cur_afectaciones = list()


    try:
        resp_parc_datos_0 = get(f"https://epok.buenosaires.gob.ar/cur3d/seccion_edificabilidad/?smp={smp[0]}")                            
        resp_parc_datos = loads(resp_parc_datos_0.text)
        band_cur_parcela.append("0")

        cur_aph = resp_parc_datos["catalogacion"]

        cur_dist_esp = resp_parc_datos["distrito_especial"]
        cur_unidad_edif = resp_parc_datos["unidad_edificabilidad"]
        cur_afectaciones_0 = resp_parc_datos["afectaciones"]

        for cur in cur_dist_esp:
            if len(cur["distrito_especifico"])>0:
                zonificacion.append(cur["distrito_especifico"])
            else:
                pass
        
        for edif in cur_unidad_edif:
            if edif == 38.0:
                zonificacion.append("C.A")
            
            elif edif == 31.2:
                zonificacion.append("C.M")
            
            elif edif == 22.8:
                zonificacion.append("U.S.A.A")
            
            elif edif == 17.2:
                zonificacion.append("U.S.A.M")

            elif edif == 11.6:
                zonificacion.append("U.S.A.B.2")

            elif edif == 9.0:
                zonificacion.append("U.S.A.B.1")
            
            else:
                pass
            
        if cur_afectaciones_0["riesgo_hidrico"]>0:
            cur_afectaciones.append("Riesgo Hídrico")
        else:
            pass
        
        if cur_afectaciones_0["lep"]>0:
            cur_afectaciones.append("Linea de Edificacion Particularizada")
        else:
            pass

        if cur_afectaciones_0["ensanche"]>0:
            cur_afectaciones.append("Afectación por Ensanche")
        else:
            pass
        
        if cur_afectaciones_0["apertura"]>0:
            cur_afectaciones.append("Afectación por Apertura")
        else:
            pass

        if cur_afectaciones_0["ci_digital"]>0:
            cur_afectaciones.append("Cinturon Digital")
        else:
            pass

        if (cur_aph["proteccion"] != None) and (cur_aph["proteccion"] != "DESESTIMADO"): 
            aph = cur_aph["proteccion"]
        else:
            aph = "No"

    except:

        band_cur_parcela.append("-1")

#FIN CONSULTA CUR PARCELA
#--- 2.7 INICIO Funciones de deteccion de campos de informes --#

def analisis_IFTAM():
    global pages_IFTAM_text
    global cubierta_3
    global mensura_3
    global plantas_3
    global semi_3
    global des_3
    global cont_3
    global particularidades
    global notas
    global notas_0
    global notas_1
    global deslinde
    global medidas
    global band_iftam_mensura
    global band_iftam_plantas
    global band_iftam_cubierta
    global band_iftam_semi
    global band_iftam_desc
    global band_iftam_prec
    global band_iftam_cont

    notas_0 = list()

    #INICIO Capturar texto de superficie de la parcela
    if 'Superficie Mts de la Parcela:' in pages_IFTAM_text: 
        index_m0 = pages_IFTAM_text.index('Superficie Mts de la Parcela: ')

    if 'Descripción de la Parcela' in pages_IFTAM_text:
        index_m1 = pages_IFTAM_text.index('Descripción de la Parcela')

    mensura_0 = pages_IFTAM_text[index_m0:index_m1].replace("Superficie Mts de la Parcela: ","")
    mensura_1 = mensura_0.replace("\n","")
    mensura_2 = mensura_1.replace(".","")
    if len(mensura_2)>0:
        mensura_3 = float(mensura_2.replace(",","."))
    else:
        mensura_3 = 0
        band_iftam_mensura = "-1"

    #INICIO Capturar texto de superficie de la parcela

    #INICIO Capturar texto de Cantidad de plantas:

    if 'Cantidad de plantas:' in pages_IFTAM_text: 
        index_p0 = pages_IFTAM_text.index('Cantidad de plantas: ')

    if 'Superficie cubierta:' in pages_IFTAM_text:
        index_p1 = pages_IFTAM_text.index('Superficie cubierta: ')

    plantas_0 = pages_IFTAM_text[index_p0:index_p1].replace("Cantidad de plantas: ","")
    plantas_1 = plantas_0.replace("\n","")
    plantas_2 = plantas_1.replace(".","")
    if len(plantas_2)>0:
        plantas_3 = float(plantas_2.replace(",","."))
    else:
        plantas_3 = 0
        band_iftam_plantas = "-1"

    #FIN Capturar texto de Cantidad de plantas:

    #INICIO Capturar texto de Superficie cubierta:

    if 'Superficie cubierta:' in pages_IFTAM_text: 
        index_c0 = pages_IFTAM_text.index('Superficie cubierta: ')

    if 'Superficie semicubierta:' in pages_IFTAM_text:
        index_c1 = pages_IFTAM_text.index('Superficie semicubierta: ')

    cubierta_0 = pages_IFTAM_text[index_c0:index_c1].replace("Superficie cubierta: ","")
    cubierta_1 = cubierta_0.replace("\n","")
    cubierta_2 = cubierta_1.replace(".","")
    if len(cubierta_2) > 0:
        cubierta_3 = float(cubierta_2.replace(",","."))
    else:
        cubierta_3 = 0
        band_iftam_cubierta = "-1"

    #FIN Capturar texto de Superficie cubierta:

    #INICIO Capturar texto de superficie semicubierta

    if 'Superficie semicubierta:' in pages_IFTAM_text: 
        index_s0 = pages_IFTAM_text.index('Superficie semicubierta: ')

    if 'Superficie descubierta:' in pages_IFTAM_text:
        index_s1 = pages_IFTAM_text.index('Superficie descubierta: ')

    semi_0 = pages_IFTAM_text[index_s0:index_s1].replace("Superficie semicubierta: ","")
    semi_1 = semi_0.replace("\n","")
    semi_2 = semi_1.replace(".","")
    if len(semi_2)>0:
        semi_3 = float(semi_2.replace(",","."))
    else:
        semi_3 = 0
        band_iftam_semi = "-1"

    # FIN Capturar texto de superficie semicubierta

    #INICIO Capturar texto de superficie Descubierta

    if 'Superficie descubierta:' in pages_IFTAM_text: 
        index_d0 = pages_IFTAM_text.index('Superficie descubierta: ')

    if 'Superficie Precaria:' in pages_IFTAM_text:
        index_d1 = pages_IFTAM_text.index('Superficie Precaria: ')

    des_0 = pages_IFTAM_text[index_d0:index_d1].replace("Superficie descubierta: ","")
    des_1 = des_0.replace("\n","")
    des_2 = des_1.replace(".","")
    if len(des_2)>0:
        des_3 = float(des_2.replace(",","."))
    else:
        des_3 = 0
        band_iftam_desc = "-1"

    # FIN Capturar texto de superficie Descubierta

    #INICIO Capturar texto de superficie Precaria

    if 'Superficie Precaria:' in pages_IFTAM_text: 
        index_pc0 = pages_IFTAM_text.index('Superficie Precaria: ')

    if 'Superficie en contravención:' in pages_IFTAM_text:
        index_pc1 = pages_IFTAM_text.index('Superficie en contravención: ')

    prec_0 = pages_IFTAM_text[index_pc0:index_pc1].replace("Superficie Precaria: ","")
    prec_1 = prec_0.replace("\n","")
    prec_2 = prec_1.replace(".","")
    if len(prec_2)>0:
        prec_3 = float(prec_2.replace(",","."))
    else:
        prec_3 = 0
        band_iftam_prec= "-1"

    # FIN Capturar texto de superficie Precaria

    #INICIO Capturar texto de superficie en contravención

    if 'Superficie en contravención:' in pages_IFTAM_text: 
        index_ct0 = pages_IFTAM_text.index('Superficie en contravención: ')

    if 'Antecedente' in pages_IFTAM_text:
        index_ct1 = pages_IFTAM_text.index('Antecedente')

    cont_0 = pages_IFTAM_text[index_ct0:index_ct1].replace("Superficie en contravención: ","")
    cont_1 = cont_0.replace("\n","")
    cont_2 = cont_1.replace(".","")
    if len(cont_2)>0:
        cont_3 = float(cont_2.replace(",","."))
    else:
        cont_3 = 0
        band_iftam_cont= "-1"
    particularidades =  re.findall(r'Particularidades: (.*?)Cantidad de plantas: ', pages_IFTAM_text)

    notas = re.findall(r'Notas: (.+)', pages_IFTAM_text, re.DOTALL)
    
    for nota in notas:
        notas_0.append((((nota.replace("","")).replace("\n","")).replace("","")).lower())
    
    notas_1 = notas_0[0].split("notas:")

    deslinde = re.findall(r"Descripción de la Parcela(.*?)Particularidades",pages_IFTAM_text,re.DOTALL)
    
    #captura las medidas de la descripcion de la parcela en una lista
    regex = r"Medida:\s*([\d(,|.)]+)\s+Tipo de Lado"
    medidas = re.findall(regex, pages_IFTAM_text)
    if len(medidas)>0:
        medidas = [float(medida.replace(",", ".")) for medida in medidas]
    else:
        pass

    # FIN Capturar texto de superficie en contravención

def analisis_IFFVN():
    global pages_IFFVN_text
    global agip_supnueva
    global agip_polig
    global agip_destinos
    global agip_supexis
    global agip_fechaconst
    global dif_agip
    global fechdemo
    global supdemo_3
    global agip_sup_nueva_exis

    agip_supnueva = list()
    agip_supexis = list()
    agip_sup_nueva_exis = list()
    supdemo_3 = 0
    fechdemo = ""


    #CAPTURAR SI DIFIERE CON AGIP

    if '¿Difiere con AGIP?: No' in pages_IFFVN_text:
        dif_agip = "no"

    elif '¿Difiere con AGIP?: Si' in pages_IFFVN_text:
        dif_agip = "si"
        
        supdemo_3 = float(re.findall(r"Superficie Demolida: (\d+,\d+)", pages_IFFVN_text)[0].replace(",", "."))
        fechdemo = re.findall(r"Fecha de Demolición: (\d{2}/\d{2}/\d{4})", pages_IFFVN_text)[0]

        if '¿¿Es Terreno Baldío?: Si' in pages_IFFVN_text:
            baldio = 'si'

            # supdemo_3 = float(re.findall(r"Superficie Demolida: (\d+,\d+)", pages_IFFVN_text)[0].replace(",", "."))
            # fechdemo = re.findall(r"Fecha de Demolición: (\d{2}/\d{2}/\d{4})", pages_IFFVN_text)[0]

            
        elif '¿Es Terreno Baldío?: No' in pages_IFFVN_text:

            #captura toda la informcacion de los distintos for,ularios declarados y los alacena en una lista por cada campo capturado
           
            agip_polig_0 =  re.findall(r'Polígonos dentro del formulario: (.*?)\nDestino: ', pages_IFFVN_text)
            agip_destinos_0 = re.findall(r'Destino:(.*)Superficie Exitente Destino:', pages_IFFVN_text)
            agip_supexis_0 = re.findall(r'Superficie Exitente Destino: (.*)Superficie Nueva / Ampliada:', pages_IFFVN_text)
            agip_supnueva_0 = re.findall(r'Superficie Nueva / Ampliada: (.*)Fecha de Construcción de Superficie nueva:', pages_IFFVN_text)
            agip_fechaconst = re.findall(r'Fecha de Construcción de Superficie nueva: (.*)Refacción del Destino:', pages_IFFVN_text)

            for i in range (len(agip_supexis_0)):
                agip_supexis_1 = agip_supexis_0[i].replace(".","")
                agip_supexis.append(float(agip_supexis_1.replace(",",".")))

                agip_supnueva_1 = agip_supnueva_0[i].replace(".","")
                agip_supnueva.append(float(agip_supnueva_1.replace(",",".")))
                agip_sup_nueva_exis.append({"sup_exist":agip_supexis,"sup_nueva":agip_supnueva})
        else:
            pass       
    else:
        pass
     
def analisis_IFDOM():
    global pages_IFDOM_text
    global sup_tit
    global inscripcion
    dom_sup = list()

    dom_insc_0 = list()
    dom_insc_1 = list()
    dom_insc = list()
    sup_tit = 0

    dom_sup_0 =  re.findall(r'Superficie en mts 2: (.*?)Descripción según título:', pages_IFDOM_text)
    dom_desc_0 = re.findall(r'Descripción según título: (.*)Restiricciones y Afectaciones Inscriptas:', pages_IFDOM_text)
    dom_rest_0 = re.findall(r'Restiricciones y Afectaciones Inscriptas: (.*)Observaciones:', pages_IFDOM_text)
    dom_obs_0 = re.findall(r'Observaciones: (.*)\¿Desea agregar otros datos de Dominio\?: ', pages_IFDOM_text)
    #dom_insc_0 = re.findall(r'Descripción Folio protocolizado\n(.*?)\n\nDatos', pages_IFDOM_text)
    dom_insc_0 = re.findall(r'Detalle matrícula(.*?)Datos|Descripción Folio protocolizado(.*?)Datos', pages_IFDOM_text, re.DOTALL)
    dom_desig_0 = re.findall(r'Designación del bien según titulo: (.*?)\nTipo de superficie de título:', pages_IFDOM_text)

    for i in range(len(dom_insc_0)): #limpia la lista de valores de dominio porque al leer el pdf se genera una lista de tuplas con valores basura ademas de la matricula o el tomo
        for dom in dom_insc_0[i]:
            if ("Matrícula:" in dom) or ("Tomo:" in dom):
                dom_insc_1.append(dom)
            else:
                pass

    for dom in dom_insc_1:
        dom_insc_2 = dom.replace("\n","")
        dom_insc.append(dom_insc_2.replace(" ",""))

    for i in range(len(dom_sup_0)): #convierte los valores numericos en números y ajusta los campos de inscripcion (elimina comas y saltos de linea leidos)
        dom_sup_1 = (dom_sup_0[i].replace(".",""))
        dom_sup.append(float(dom_sup_1.replace(",",".")))
        sup_tit = sup_tit  + dom_sup[i]

#--- 2.7 FIN Funciones de deteccion de campos de informes --#
                    
#--- 2 FIN Validación del Archivo DXF ---#

#--- 3 INICIO EXPORTAR PDF CON RESUMEN  ---#
def salida_pdf():
    global smp
    global validaciones2
    global comparacion

    validaciones3 = DataFrame(columns=['N°','Observacion'])
    
    for i in range(len(validaciones2)):
        validaciones3.loc[i,"N°"] = i
        validaciones3.loc[i,"Observacion"] = validaciones2.loc[i,"Observacion"]
        

    if len(validaciones3)>0:

        directorio = filedialog.askdirectory()

        if len(smp):
            c = canvas.Canvas(directorio + f"/validacion_dxf_{smp[0]}.pdf",pagesize=A4)
            smp_hoja = smp[0]

        else:
            c = canvas.Canvas(directorio + "/validacion_dxf_sinSMP.pdf",pagesize=A4)
            smp_hoja = "Sin SMP declarada"
        c.setFont("Times-Roman", 12)
        #Datos que se imprimiran en el pdf
        texto_encabezado=["Subgerencia Operativa de Registro de Mensura",
                          "Gerencia Operativa de Catastro Físico",
                          "Dirección General de Registro de Obras y Catastro"]

        #Impresión en canvas
        c.drawString(175, 800,  texto_encabezado[0])
        c.drawString(175, 780,  texto_encabezado[1])
        c.drawString(175, 760,  texto_encabezado[2])

        #Linea Separadora
        c.line(50, 740, 550, 740)

        c.drawString(175, 720,  f"Resultado Validación Archivo DXF Parcela:{smp_hoja}")
        #Encabezados de tabla
        c.drawString(20, 700, 'N°')
        c.drawString(50, 700, 'Observacion')

        #Filas de tabla
        i=int(680)
        c.setFont("Times-Roman", 9)
        c.setFillColorRGB(1,1,1)
        # for index, row in validaciones3.iterrows():
        for k in range (len(validaciones3)):
            if "Error:" in validaciones3.loc[k,'Observacion'] or "ERROR:" in validaciones3.loc[k,'Observacion'] or "error:" in validaciones3.loc[k,'Observacion']:
                c.setFillColorRGB(1,0.62,0.62)
            elif "Verificar:" in validaciones3.loc[k,'Observacion'] or "VERIFICAR:" in validaciones3.loc[k,'Observacion'] or "verificar" in validaciones3.loc[k,'Observacion']:
                c.setFillColorRGB(1,0.74,0.45)
            elif "OK" in validaciones3.loc[k,'Observacion'] or "Ok" in validaciones3.loc[k,'Observacion'] or "ok" in validaciones3.loc[k,'Observacion']:
                c.setFillColorRGB(0.68,1,0.62)
            else:
                c.setFillColorRGB(1,1,1)
            #dibuja rectangulo del fondo del texto de la validacion
            c.rect(18,i-5,565,20,stroke=1,fill=1)
            #cambia color a negro para el texto
            c.setFillColorRGB(0,0,0)
            #inserta el texto
            c.drawString(20, i, str(validaciones3.loc[k,'N°']))
            c.drawString(50, i, str(validaciones3.loc[k,'Observacion']))
            i-=20

            if i <= 20:
                c.showPage()
                i=int(680)

                #Impresión en canvas
                c.drawString(175, 800,  texto_encabezado[0])
                c.drawString(175, 780,  texto_encabezado[1])
                c.drawString(175, 760,  texto_encabezado[2])

                #Linea Separadora
                c.line(50, 740, 550, 740)
                
                c.drawString(175, 720,  f"Resultado Validación Archivo DXF Parcela:{smp_hoja}")
                #Encabezados de tabla
                c.drawString(20, 700, 'N°')
                c.drawString(50, 700, 'Observacion')

                #Filas de tabla
                i=680
                c.setFont("Times-Roman", 9)
                c.setFillColorRGB(1,1,1)
            else:
                pass 
        c.save() 
        print("Archivo PDF generado exitosamente en " + directorio)
                          
    else:
        print(messagebox.showerror(message="Primero debe cargar y procesar el archivo antes de exportar el reumen", title="Error"))
##

#--- 3 FIN EXPORTAR PDF CON RESUMEN  ---#


Boton_Chequear_layers= Button(marco5, text="Procesar DXF CEP", command=Procesar_Archivo)
Boton_Chequear_layers.configure(font=("Gotham Rounded",8))
Boton_Chequear_layers.grid(padx=5, pady=2, row = 0, column=0)


##Boton_Generar_Resumen= Button(marco5, text="Generar Resumen", command=Generar_Resumen).pack()

raiz.mainloop()

