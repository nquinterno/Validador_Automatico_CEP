import ezdxf
from ezdxf import recover
from os import path
from tkinter import messagebox, filedialog, ttk
from pandas import DataFrame
from PyPDF2 import PdfReader

global last_dir
last_dir = ""

def Abrir_Archivo_dxf(pages_IFTAM_text,pages_IFDOM_text,pages_IFFVN_text,pages_FOMUBI_text):

    pages_IFTAM_text,pages_IFDOM_text,pages_IFFVN_text,pages_FOMUBI_text = "","","",""
    global last_dir
    last_dir = ""
    
    try:
        if last_dir != "":
            ruta = filedialog.askopenfilename(title="abrir", initialdir=f"{last_dir}")
            doc, auditor = recover.readfile(ruta)
            
        else:
            ruta = filedialog.askopenfilename(title="abrir", initialdir="C:/")
            doc, auditor = recover.readfile(ruta)
            last_dir = path.abspath(ruta)
        return doc,pages_IFTAM_text,pages_IFDOM_text,pages_IFFVN_text,pages_FOMUBI_text
    
    except IOError:
        exit(1)
        

    except ezdxf.DXFStructureError:
        print(messagebox.showerror(message="El archivo selecciondo no es un archivo DXF o el mismo esta corrupto", title="Error"))
        exit(2)

def Abrir_Archivo_IFTAM():
    global pages_IFTAM_text
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
                documento_1.stream.close() 
                return pages_IFTAM_text

            else:
                print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Mensura", title="Error"))
                documento_1.stream.close() 
        else:
            print(messagebox.showerror(message="El archivo selecciondo no es un archivo pdf", title="Error"))
    except IOError:
        exit(1)

def Abrir_Archivo_IFDOM():
    global pages_IFDOM_text
    global last_dir
    # global comparacion
    # global validaciones
    # comparacion = DataFrame()
    # comparacion = validaciones.drop(['Validacion','Descripcion',],axis='columns')
    
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
                documento_1.stream.close() 
                return pages_IFDOM_text
            else:
                documento_1.stream.close() 
                return(print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Dominio", title="Error")))          
        else:
            return(print(messagebox.showerror(message="El archivo selecciondo no es un archivo pdf", title="Error")))

    except IOError:
        exit(1)

def Abrir_Archivo_IFFVN():
    global pages_IFFVN_text
    global last_dir

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
                documento_1.stream.close() 
                return pages_IFFVN_text

            else:
                print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Resumen", title="Error"))
                documento_1.stream.close()            
        else:
            print(messagebox.showerror(message="El archivo selecciondo no es un archivo pdf", title="Error"))

    except IOError:
        exit(1)

def Abrir_Archivo_FOMUBI():
    global last_dir
    global pages_FOMUBI_text
    
    try:

        if last_dir != "":
            documento = filedialog.askopenfilename(title="abrir Formulario Ubicación", initialdir=f"{last_dir}")
        else:
            documento = filedialog.askopenfilename(title="abrir Formulario Ubicación", initialdir="C:/")
            last_dir = path.abspath(documento)
      
        if documento.endswith(".pdf"):
            documento_1 = PdfReader(documento)
            num_pages_doc1 = len(documento_1.pages)
            pages_doc1_text = "" 

            for page_num in range(num_pages_doc1):
                pages_doc1_text += (documento_1.pages[page_num]).extract_text()

            if 'Formulario de Ubicación' in pages_doc1_text:
                pages_FOMUBI_text = pages_doc1_text
                documento_1.stream.close()
                return pages_FOMUBI_text
            else:
                documento_1.stream.close()
                print(messagebox.showerror(message="El archivo pdf seleccionado no es un formulario de Ubicación", title="Error"))         
        else:
            print(messagebox.showerror(message="El archivo selecciondo no es un archivo .pdf", title="Error"))

    except IOError:
        exit(1)

