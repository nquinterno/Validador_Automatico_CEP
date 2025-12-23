## Validador Automàtico de CEP (VAC) Copyright (C) <2022> <Ing. Agrim Nicolás Quinterno>

##--------------------------------------------------------------------------------------------

## Este programa permite Validar de manera Automatica distintos aspectos de los planos de Constitución de estado parcelario
## que deban presentarse ante la Subgerencia Operativa de Registro de Mensuras - Gerencia Operativa
## de Catastro Fìsico - DGROC - GCBA, en formato DXF.

## Valida entre otros aspectos:
    ## * Coherencia y completitud y correcta representación de datos indicados en el espacio modelo
    ## * Coherencia entre los elementos representados en el model y los datos asociados del resto del archivo
    ## * Correcta georreferenciación de la parcela mensurada comparando con el servicio de Ciudad3d
    ## * Difereniamentre los vertices de la parcela registrada en las basses de datos catastrales y la parcela medida
    ## * Coherencia en los datos indicados en los fromularios pdf que se cargarán en el tramite TAD en relación con la información extraida del archivo dxf, tal como Superficie de la parcela, excedente, superficie cubierta, semicubierta, descubierta, cantidad de plantas, restricciones, etc.

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
from procesamiento.main_procesamiento import Procesar_Archivo, carga_IFTAM, carga_IFFVN, carga_IFDOM, cargar_doc, carga_FOMUBI, descarga_vectores, descarga_Informe_pdf, muestra_resumen
from salidas.Cep.informe import *
from procesamiento.General.procesamiento_georref import *
from salidas.resumen import *
from pandas import read_csv

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
marco3.config(width="100",height="60")
marco3.grid(padx=5, pady=3, row = 0, column=0)

marco4 = Frame(marco1)
marco4.config(width="400",height="60")
marco4.grid(padx=5, pady=3, row = 0, column=2)

marco5 = Frame(marco1)
marco5.config(width="200",height="60")
marco5.grid(padx=5, pady=3, row = 0, column=3)

marco6 = Frame(marco1)
marco6.config(width="100",height="60")
marco6.grid(padx=5, pady=3, row = 0, column=1)

marco7 = Frame(marco1)
marco7.config(width="400",height="20")
marco7.grid(padx=5, pady=0, row = 1, column=2)


version = read_csv('configuracion/version.csv').at[0,'Version']

label = Label(marco4,text=f"VAC - (Validador Automatico CEP) - Versión {version}")
label.configure(font=("Gotham Rounded",8))
label.grid(padx=25, pady=2, row = 0, column=1)

label1 = Label(marco4,text="Subgerencia Operativa de Registro de Mensuras\nGerencia Operativa de Catastro Físico\nDirección General de Registro de Obras y Catastro")
label1.configure(font=("Gotham Rounded",8))
label1.grid(padx=25, pady=2, row = 1, column=1)

label2 = Label(marco4,text="Importante!: 1° cargar dxf, 2° cargar forms.\n 3° procesar, 4° descragar pdf")
label2.configure(font=("Gotham Rounded",8),fg="red")
label2.grid(padx=5, pady=2, row = 2, column=1)

tv = ttk.Treeview(marco2, height=20)
tv['columns']=("Nº","Validacion")
tv.column("#0", width="0", stretch="NO")
tv.column("Validacion",anchor="w", width="750")
tv.column("Nº",anchor="w", width="25")
tv.heading("Validacion",text="Validación",anchor="w")
tv.heading("Nº",text="Nº",anchor="w")

verscrlbar = ttk.Scrollbar(marco2, orient="vertical", command=tv.yview)
tv.configure(yscrollcommand = verscrlbar.set)
verscrlbar.pack(side ='right', fill ='y')        

tv.pack(fill="both", expand=True)

def descarga_pdf():
    descarga_Informe_pdf(opcion)

btn_pdf = Button(marco5,text="Descargar Resultados en PDF", command=descarga_pdf)
btn_pdf.configure(font=("Gotham Rounded",8))

btn_descargar = Button(marco5,text="Descargar vectores DXF", command=descarga_vectores)
btn_descargar.configure(font=("Gotham Rounded",8))

btn_resumen = Button(marco5,text="Resumen DXF", command=muestra_resumen)
btn_resumen.configure(font=("Gotham Rounded",8))

def carga_tv():
    global opcion
    validaciones2_f  = Procesar_Archivo(opcion, opcion_mens)
    
    tv.tag_configure(tagname="error",background = "#FEA9A9")
    tv.tag_configure(tagname="ok",background = "#ADFEA9")
    tv.tag_configure(tagname='NaN',background = "light grey")
    tv.tag_configure(tagname='precaucion',background = "orange")

    for i in tv.get_children():
        tv.delete(i)
    
    for i in range (0,len(validaciones2_f)):
        if  validaciones2_f.loc[i,'Resultado']== 0:
            tv.insert('',END,values=(i,validaciones2_f.loc[i,'Observacion']),tags=["ok",])

        elif validaciones2_f.loc[i,'Resultado'] <0:
            tv.insert('',END,values=(i,validaciones2_f.loc[i,'Observacion']),tags=["error",])

        elif validaciones2_f.loc[i,'Resultado'] ==50:
            tv.insert('',END,values=(i,validaciones2_f.loc[i,'Observacion']),tags=["precaucion",])
        elif validaciones2_f.loc[i,'Resultado'] ==99:
            tv.insert('',END,values=(i,validaciones2_f.loc[i,'Observacion']),tags=["NaN",])
        else:
            pass

    # btn_resumen = Button(marco5,text="Resumen DXF", command=muestra_resumen)
    # btn_resumen.configure(font=("Gotham Rounded",8))
    # btn_resumen.grid(padx=5, pady=2, row = 1, column=0)

    # btn_descargar = Button(marco5,text="Descargar vectores DXF", command=descarga_vectores)
    # btn_descargar.configure(font=("Gotham Rounded",8))
    # btn_descargar.grid(padx=5, pady=2, row = 2, column=0)

    # btn_pdf = Button(marco5,text="Descargar Resultados en PDF", command=descarga_pdf)
    # btn_pdf.configure(font=("Gotham Rounded",8))

    if "grid" in btn_pdf.winfo_manager():
        pass
    else:
        btn_pdf.grid(padx=5, pady=2, row = 3, column=0)
    
    if "grid" in btn_descargar.winfo_manager():
        pass
    else:
        btn_descargar.grid(padx=5, pady=2, row = 2, column=0)

    if "grid" in btn_resumen.winfo_manager():
        pass
    else:
        btn_resumen.grid(padx=5, pady=2, row = 1, column=0) 
    

abrir_dxf = Button(marco3, text="Abrir DXF", command=cargar_doc)
abrir_dxf.configure(font=("Gotham Rounded",8))

abrir_FOMUBI = Button(marco6, text="Abrir Form. Ubicacíon", command=carga_FOMUBI)
abrir_FOMUBI.configure(font=("Gotham Rounded",8))

abrir_IFTAM = Button(marco6, text="Abrir Form Mensura", command=carga_IFTAM)
abrir_IFTAM.configure(font=("Gotham Rounded",8))

abrir_IFDOM = Button(marco6, text="Abrir Form Dominio", command=carga_IFDOM)
abrir_IFDOM.configure(font=("Gotham Rounded",8))

abrir_IFFVN = Button(marco6, text="Abrir Form Resumen", command=carga_IFFVN)
abrir_IFFVN.configure(font=("Gotham Rounded",8))

label3 = Label(marco3,text="proximamente")
label3.configure(font=("Gotham Rounded",8),fg="red")

label4 = Label(marco5,text="proximamente")
label4.configure(font=("Gotham Rounded",8),fg="red")

Boton_Procesar_CEP = Button(marco5, text="Procesar DXF CEP", command = carga_tv)
Boton_Procesar_CEP.configure(font=("Gotham Rounded",8))

Boton_Procesar_Legajo = Button(marco5, text="Procesar DXF CEP", command = carga_tv)
Boton_Procesar_Legajo.configure(font=("Gotham Rounded",8))

Boton_Procesar_Mensura = Button(marco5, text="Procesar Mensura", command = carga_tv)
Boton_Procesar_Mensura.configure(font=("Gotham Rounded",8))

opcion = IntVar()
opcion_mens = IntVar()


def botonera_mensura():

    global abrir_FOMUBI, abrir_IFTAM, abrir_IFDOM, abrir_IFFVN, Boton_Procesar_CEP, Boton_Procesar_Legajo, Boton_Procesar_Mensura, abrir_dxf, label3, label4, opcion_Mensura_simple_Pos, opcion_MH_Nuevo, opcion_Unificación, opcion_Fraccionamiento, opcion_Redistribución, opcion_Posesion_unidad, opcion_Modificacion_MH
    
    # label3 = Label(marco3,text="proximamente")
    # label3.configure(font=("Gotham Rounded",8),fg="red")
    # label3.grid(padx=5, pady=2, row = 1, column=0)

    # label4 = Label(marco5,text="proximamente")
    # label4.configure(font=("Gotham Rounded",8),fg="red")
    # label4.grid(padx=5, pady=2, row = 0, column=0)

    if "grid" in btn_descargar.winfo_manager():
        btn_descargar.grid_forget()
    else:
        pass

    if "grid" in btn_resumen.winfo_manager():
        btn_resumen.grid_forget()
    else:
        pass

    if "grid" in btn_pdf.winfo_manager():
        btn_pdf.grid_forget()
    else:
        pass

    if "grid" in abrir_dxf.winfo_manager():
        abrir_dxf.grid_forget()
    else:
        pass

    if "grid" in Boton_Procesar_CEP.winfo_manager():
       Boton_Procesar_CEP.grid_forget()
    else:
        pass

    if "grid" in Boton_Procesar_Legajo.winfo_manager():
        Boton_Procesar_Legajo.grid_forget()
    else:
        pass

    if "grid" in abrir_IFDOM.winfo_manager():
        abrir_IFDOM.grid_forget()
    else:
        pass

    if "grid" in abrir_IFFVN.winfo_manager():
        abrir_IFFVN.grid_forget()
    else:
        pass

    if "grid" in abrir_FOMUBI.winfo_manager():
        abrir_FOMUBI.grid_forget()
    else:
        pass
    
    if "grid" in abrir_IFTAM.winfo_manager():
        abrir_IFTAM.grid_forget()
    else:
        pass

    #Prende y apaga las opciones de Mensura para validar

    if "grid" in opcion_Mensura_simple_Pos.winfo_manager():
        pass
    else:
        opcion_Mensura_simple_Pos.grid(padx=0, pady=0, row = 0, column=0)

    if "grid" in opcion_MH_Nuevo.winfo_manager():
        pass
    else:
        opcion_MH_Nuevo.grid(padx=0, pady=0, row = 1, column=0)

    if "grid" in opcion_Unificación.winfo_manager():
        pass
    else:
        opcion_Unificación.grid(padx=0, pady=0, row = 2, column=0)
    
    if "grid" in opcion_Fraccionamiento.winfo_manager():
        pass
    else:
        opcion_Fraccionamiento.grid(padx=0, pady=0, row = 3, column=0)
   
    if "grid" in opcion_Redistribución.winfo_manager():
        pass
    else:
        opcion_Redistribución.grid(padx=0, pady=0, row = 4, column=0)
    if "grid" in opcion_Posesion_unidad.winfo_manager():
        pass
    else:
        opcion_Posesion_unidad.grid(padx=0, pady=0, row = 5, column=0)
    if "grid" in opcion_Modificacion_MH.winfo_manager():
        pass
    else:
        opcion_Modificacion_MH.grid(padx=0, pady=0, row = 6, column=0)

    if "grid" in label2.winfo_manager():
        label2.grid_forget()
    else:
        pass

    if "grid" in abrir_dxf.winfo_manager():
        pass
    else:
        abrir_dxf.grid(padx=5, pady=2, row = 1, column=0)

    Boton_Procesar_Mensura = Button(marco5, text="Procesar Mensura", command = carga_tv)
    Boton_Procesar_Mensura.configure(font=("Gotham Rounded",8))
    Boton_Procesar_Mensura.grid(padx=5, pady=2, row = 0, column=0)

def botonera_cep():

    global abrir_FOMUBI, abrir_IFTAM, abrir_IFDOM, abrir_IFFVN, Boton_Procesar_CEP, Boton_Procesar_Legajo, Boton_Procesar_Mensura, abrir_dxf, label3, label4

    if "grid" in btn_descargar.winfo_manager():
        btn_descargar.grid_forget()
    else:
        pass

    if "grid" in btn_resumen.winfo_manager():
        btn_resumen.grid_forget()
    else:
        pass

    if "grid" in btn_pdf.winfo_manager():
        btn_pdf.grid_forget()
    else:
        pass

    if "grid" in label4.winfo_manager():
        label4.grid_forget()
    else:
        pass

    if "grid" in label3.winfo_manager():
        label3.grid_forget()
    else:
        pass

    if "grid" in Boton_Procesar_Mensura.winfo_manager():
        Boton_Procesar_Mensura.grid_forget()
    else:
        pass

    if "grid" in Boton_Procesar_Legajo.winfo_manager():
        Boton_Procesar_Legajo.grid_forget()
    else:
        pass

    # abrir_dxf = Button(marco3, text="Abrir DXF", command=cargar_doc)
    # abrir_dxf.configure(font=("Gotham Rounded",8))
    
    if "grid" in abrir_dxf.winfo_manager():
        pass
    else:
        abrir_dxf.grid(padx=5, pady=2, row = 1, column=0)
    
    if "grid" in abrir_FOMUBI.winfo_manager():
        pass
    else:
        abrir_FOMUBI.grid(padx=5, pady=2, row = 3, column=0)
    
    if "grid" in abrir_IFFVN.winfo_manager():
        pass
    else:
        abrir_IFFVN.grid(padx=5, pady=2, row = 1, column=0)
    
    if "grid" in abrir_IFDOM.winfo_manager():
        pass
    else:
        abrir_IFDOM.grid(padx=5, pady=2, row = 2, column=0)

    if "grid" in abrir_IFTAM.winfo_manager():
        pass
    else:
        abrir_IFTAM.grid(padx=5, pady=2, row = 0, column=0)

    
    #Apaga la sopciones de Mensura
    if "grid" in opcion_Mensura_simple_Pos.winfo_manager():
        opcion_Mensura_simple_Pos.grid_forget()
    else:
        pass
    if "grid" in opcion_MH_Nuevo.winfo_manager():
        opcion_MH_Nuevo.grid_forget()
    else:
        pass
    if "grid" in opcion_Unificación.winfo_manager():
        opcion_Unificación.grid_forget()
    else:
        pass
    if "grid" in opcion_Fraccionamiento.winfo_manager():
        opcion_Fraccionamiento.grid_forget()
    else:
        pass
    if "grid" in opcion_Redistribución.winfo_manager():
        opcion_Redistribución.grid_forget()
    else:
        pass
    if "grid" in opcion_Posesion_unidad.winfo_manager():
        opcion_Posesion_unidad.grid_forget()
    else:
        pass
    if "grid" in opcion_Modificacion_MH.winfo_manager():
        opcion_Modificacion_MH.grid_forget()
    else:
        pass

    Boton_Procesar_CEP = Button(marco5, text="Procesar CEP", command = carga_tv)
    Boton_Procesar_CEP.configure(font=("Gotham Rounded",8))
    Boton_Procesar_CEP.grid(padx=5, pady=2, row = 0, column=0)

def botonera_legajo():

    global abrir_FOMUBI, abrir_IFTAM, abrir_IFDOM, abrir_IFFVN, Boton_Procesar_CEP, Boton_Procesar_Legajo, Boton_Procesar_Mensura,label3, label4

    if "grid" in btn_descargar.winfo_manager():
        btn_descargar.grid_forget()
    else:
        pass

    if "grid" in btn_resumen.winfo_manager():
        btn_resumen.grid_forget()
    else:
        pass

    if "grid" in btn_pdf.winfo_manager():
        btn_pdf.grid_forget()
    else:
        pass

    if "grid" in label4.winfo_manager():
        label4.grid_forget()
    else:
        pass

    if "grid" in label3.winfo_manager():
        label3.grid_forget()
    else:
        pass

    if "grid" in abrir_FOMUBI.winfo_manager():
        abrir_FOMUBI.grid_forget()
    else:
        pass

    if "grid" in Boton_Procesar_CEP.winfo_manager():
        Boton_Procesar_CEP.grid_forget()
    else:
        pass

    if "grid" in Boton_Procesar_Mensura.winfo_manager():
        Boton_Procesar_Mensura.grid_forget()
    else:
        pass


    if "grid" in abrir_dxf.winfo_manager():
        pass
    else:
        abrir_dxf.grid(padx=5, pady=2, row = 1, column=0)
    
    if "grid" in abrir_IFFVN.winfo_manager():
        pass
    else:
        abrir_IFFVN.grid(padx=5, pady=2, row = 1, column=0)
    
    if "grid" in abrir_IFDOM.winfo_manager():
        pass
    else:
        abrir_IFDOM.grid(padx=5, pady=2, row = 2, column=0)

    if "grid" in abrir_IFTAM.winfo_manager():
        pass
    else:
        abrir_IFTAM.grid(padx=5, pady=2, row = 0, column=0)


    #Apaga la sopciones de Mensura
    if "grid" in opcion_Mensura_simple_Pos.winfo_manager():
        opcion_Mensura_simple_Pos.grid_forget()
    else:
        pass
    if "grid" in opcion_MH_Nuevo.winfo_manager():
        opcion_MH_Nuevo.grid_forget()
    else:
        pass
    if "grid" in opcion_Unificación.winfo_manager():
        opcion_Unificación.grid_forget()
    else:
        pass
    if "grid" in opcion_Fraccionamiento.winfo_manager():
        opcion_Fraccionamiento.grid_forget()
    else:
        pass
    if "grid" in opcion_Redistribución.winfo_manager():
        opcion_Redistribución.grid_forget()
    else:
        pass
    if "grid" in opcion_Posesion_unidad.winfo_manager():
        opcion_Posesion_unidad.grid_forget()
    else:
        pass
    if "grid" in opcion_Modificacion_MH.winfo_manager():
        opcion_Modificacion_MH.grid_forget()
    else:
        pass

    Boton_Procesar_Legajo = Button(marco5, text="Procesar Legajo", command = carga_tv)
    Boton_Procesar_Legajo.configure(font=("Gotham Rounded",8))
    Boton_Procesar_Legajo.grid(padx=5, pady=2, row = 0, column=0)



opcion_cep = Radiobutton(marco7, text="CEP", variable=opcion, value="1", command=botonera_cep)
opcion_cep.grid(padx=0, pady=0, row = 0, column=0)

opcion_legajo = Radiobutton(marco7, text="Legajo", variable=opcion, value="2", command=botonera_legajo)
opcion_legajo.grid(padx=0, pady=0, row = 0, column=1)

opcion_mensura = Radiobutton(marco7, text="Mensura", variable=opcion, value="3", command=botonera_mensura)
opcion_mensura.grid(padx=0, pady=0, row = 0, column=2)

opcion_Mensura_simple_Pos = Radiobutton(marco6, text="Mens. Simp./Pos.", variable=opcion_mens, value="4", command=lambda:None)
opcion_MH_Nuevo = Radiobutton(marco6, text="MH-NUEVO", variable=opcion_mens, value="5", command=lambda:None)
opcion_Unificación = Radiobutton(marco6, text="Unificación", variable=opcion_mens, value="6", command=lambda:None)
opcion_Fraccionamiento = Radiobutton(marco6, text="Fraccionamiento", variable=opcion_mens, value="7", command=lambda:None)
opcion_Redistribución = Radiobutton(marco6, text="Redistribución", variable=opcion_mens, value="8", command=lambda:None)
opcion_Posesion_unidad = Radiobutton(marco6, text="POS. UF/UC", variable=opcion_mens, value="9", command=lambda:None)
opcion_Modificacion_MH = Radiobutton(marco6, text="Modif. MH", variable=opcion_mens, value="10", command=lambda:None)


raiz.mainloop()
