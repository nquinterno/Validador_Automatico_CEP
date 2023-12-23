from procesamiento.procesamiento_archivo import *
from procesamiento.procesamiento_layers import *
from procesamiento.procesamiento_bloques import *
from procesamiento.procesamiento_cotas import *
from procesamiento.procesamiento_layout import *
from procesamiento.procesamiento_model import *
from procesamiento.procesamiento_formularios import *
from procesamiento.procesamiento_cur import *
from procesamiento.procesamiento_georref import *
from procesamiento.carga_archivos import *
from procesamiento.comparacion_formularios_cep import *
from procesamiento.comparacion_formularios_legajo import *
from salidas.informe import *
from procesamiento.comparacion_formularios_cep import *
from pandas import DataFrame, read_excel, concat, read_csv
from tkinter import*
from tkinter import messagebox
from salidas.descargar_dxf import *
from salidas.resumen import *


global doc_f
global version

version = read_csv('configuracion/version.csv').at[0,'Version']

#declaracion como globales e inicializacion de las variables del IFFTAM
global pages_IFTAM_text
global particularidades_f, notas_1_f, des_3_f, semi_3_f, cubierta_3_f, plantas_3_f, mensura_3_f, cont_3_f, medidas_f

pages_IFTAM_text = ""
particularidades_f, notas_1_f, medidas_f = "", "", ""
des_3_f, semi_3_f, cubierta_3_f, plantas_3_f, mensura_3_f, cont_3_f = 0 ,0, 0, 0, 0, 0


#declaracion como globales e inicializacion de las variables del IFFVN
global pages_IFFVN_text
global dif_agip_f, baldio_f, supdemo_3_f, fechdemo_f, agip_supnueva_f, agip_fechaconst_f ,agip_supexis_f, agip_sup_nueva_exis_f

dif_agip_f, baldio_f, fechdemo_f, agip_fechaconst_f = "", "" ,"" ,""
supdemo_3_f, agip_supnueva_f, agip_supexis_f, agip_sup_nueva_exis_f = 0 ,0, 0, 0
pages_IFFVN_text = ""


#declaracion como globales e inicializacion de las variables del IFDOM
global dom_insc_f
global sup_tit_f
global pages_IFDOM_text
pages_IFDOM_text = ""

dom_insc_f = ""
sup_tit_f = 0

#declaracion como globales e inicializacion de las variables del procesamiento del model
global lados_parcelas_l_f,excedentes_poly_f, piso_con_mejoras_f, info_form_emp_f, info_form_nuevo_f
#global medidas_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, parcelas_poly_f
#declaracion como globales e inicializacion de las variables del procesamiento del layout
global smp_f

#declaracion como globales e inicializacion de las variables del procesamiento de la georreferenciacion
global dif_max_f

#declaracion como globales e inicializacion de las variables del procesamiento de los datos del CUR
global cur_afectaciones_f, aph_f, zonificacion_f

#declaracion de global variables de validaciones 
# global validaciones_archivo, validaciones_layer, validaciones_bloques, validaciones_model, validaciones_cotas, validaciones_layout, validaciones_georref

pages_FOMUBI_text = ""

def cargar_doc():
    global doc_f,pages_IFTAM_text,pages_IFDOM_text,pages_IFFVN_text,pages_FOMUBI_text
    doc_f,pages_IFTAM_text,pages_IFDOM_text,pages_IFFVN_text,pages_FOMUBI_text = Abrir_Archivo_dxf(pages_IFTAM_text,pages_IFDOM_text,pages_IFFVN_text,pages_FOMUBI_text)

def carga_IFTAM():
    global pages_IFTAM_text
    pages_IFTAM_text = Abrir_Archivo_IFTAM()


def carga_IFFVN():

    global pages_IFFVN_text
    pages_IFFVN_text = Abrir_Archivo_IFFVN()

def carga_IFDOM():
    global pages_IFDOM_text
    pages_IFDOM_text = Abrir_Archivo_IFDOM()

def carga_FOMUBI():
    global pages_FOMUBI_text
    pages_FOMUBI_text = Abrir_Archivo_FOMUBI()
    

def descarga_vectores():
    global last_dir,parcelas_poly, manz_ant_posgba_2,parc_ant_posgba_2
    descargar_dxf(last_dir, parcelas_poly, manz_ant_posgba_2,parc_ant_posgba_2)

# def descargar_informe():
#     pass

def muestra_resumen():
    global smp_f, area_parc_dxf, area_excedente_dxf, plantas_dxf_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_emp_dxf_f, sup_nueva_dxf_f

    mostrar_resumen(smp_f, area_parc_dxf, area_excedente_dxf, plantas_dxf_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_emp_dxf_f, sup_nueva_dxf_f)


def descarga_Informe_pdf(opcion):
    global validaciones2,parcelas_poly,parc_ant_posgba_2,manz_ant_posgba_2,smp_f,smp_fomubi,exp_layout_f,exp_fomubi, medidas_dxf_f, lados_iftam, cubierta_3_f, mensura_3_f, plantas_3_f, semi_3_f, des_3_f, cont_3_f, area_parc_dxf, area_excedente_dxf, piso_con_mejoras_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_emp_dxf_f, sup_nueva_dxf_f,version,resultado_final

    salida_pdf(opcion,validaciones2,parcelas_poly,parc_ant_posgba_2,manz_ant_posgba_2,smp_f,smp_fomubi,exp_layout_f,exp_fomubi, medidas_dxf_f, lados_iftam, cubierta_3_f, mensura_3_f, plantas_3_f, semi_3_f, des_3_f, cont_3_f, area_parc_dxf, area_excedente_dxf, piso_con_mejoras_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_emp_dxf_f, sup_nueva_dxf_f,version,resultado_final)


def Procesar_Archivo(opcion):
    global doc_f
    global last_dir
    global validaciones2

    #declaracion de global texto de formularios
    global pages_IFDOM_text
    global pages_IFFVN_text
    global pages_IFTAM_text
    global pages_FOMUBI_text

    #declaracion de global variables del proceamiento model
    global lados_parcelas_l_f,excedentes_poly_f, piso_con_mejoras_f, info_form_emp_f, info_form_nuevo_f, parcelas_poly, medidas_dxf_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f
    #global medidas_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, parcelas_poly_f

    #declaracion de global variables del proceamiento georreferenciacion
    global dif_max_f

    #declaracion de global del proceamiento layout
    global smp_f
    global exp_layout_f
    #declaracion de global variables del proceamiento cur  
    global cur_afectaciones_f, aph_f, zonificacion_f

    #declaracion de global variables de validaciones 
    global validaciones_archivo, validaciones_layer, validaciones_bloques, validaciones_model, validaciones_cotas, validaciones_layout, validaciones_georref, validaciones_extra
        
    global nom_layers_dxf

    global parc_ant_posgba_2, manz_ant_posgba_2

    global particularidades_f, notas_1_f, cont_3_f, des_3_f, semi_3_f, cubierta_3_f, plantas_3_f, mensura_3_f, medidas_f,lados_iftam

    #declaracion de global variables de coparacion con formularios
    global  lados_iftam, smp_fomubi, exp_fomubi,area_parc_dxf, area_excedente_dxf ,resultado_final, sup_emp_dxf_f, sup_nueva_dxf_f, plantas_dxf_f

    validaciones = DataFrame()
    validaciones2 = DataFrame()

    filas_con_error = list()
    band_filas_error = list()

    validaciones = read_excel('configuracion/config_validaciones.xls') #data frame con archivo de Configuración de validaciones xls
    validaciones2 = validaciones.drop(['Validacion','Descripcion',],axis='columns') #borra columnas innecesarias del data frame validaciones
    colores = read_csv('configuracion/colores.csv')
    # global sup_parc_poly #superficie de parcelas
    # global sup_ces_poly #superficie de cesión
    # global sup_mens_poly #superficie de mensura calculada como la suma de parcelas y cesiones
    global parcelas_poly_close #parcelas polilineas cerradas
    global mejoras_poly #poligonos de mejoras polilinea
    
    global resultado_final
    # sup_parc_poly = 0
    # sup_ces_poly = 0
    # sup_mens_poly = 0
    # lados_parcelas_l = list()

    if doc_f != "":
        #model = doc.modelspace() #inserta el model espace en la variable model
        
        model = doc_f.modelspace() #inserta el model espace en la variable model
        layouts = doc_f.layout_names()
        layouts.remove('Model') # crea una lista con los nombres de los layouts borrando el nombre dle model

        validaciones_archivo = chequeo_archivo(doc_f)
        
        validaciones_layer, nom_layers_dxf= chequeo_layers(doc_f)
        
        validaciones_bloques =  chequeo_bloques(doc_f)
        
        validaciones_model, medidas_dxf_f,parcelas_poly_close_f,parcelas_poly,excedentes_poly, mejoras_dict,band_dict, nom_parc_list  = chequeo_model(doc_f, nom_layers_dxf, colores)


        piso_con_mejoras_f = mejoras_dict["piso_con_mejoras"]
        info_form_emp_f = mejoras_dict["info_form_emp"]
        info_form_nuevo_f =  mejoras_dict["info_form_nuevo"]
        layers_mejoras_spb = mejoras_dict["layers_mejoras_spb"]
        sup_cub_dxf_f = mejoras_dict["sup_cub_dxf"]
        sup_semicub_dxf_f =  mejoras_dict["sup_semicub_dxf"]
        sup_descub_dxf_f = mejoras_dict["sup_descub_dxf"]
        sup_descont_dxf_f = mejoras_dict["sup_descont_dxf"]

        
        band_mejora_cub_arc_0 = band_dict["band_mejora_cub_arc"]
        band_mejora_semi_arc_0 = band_dict["band_mejora_semi_arc"]
        band_mejora_desc_arc_0 = band_dict["band_mejora_desc_arc"]
        band_mejora_emp_arc_0 = band_dict["band_mejora_emp_arc"]
        band_mejora_nueva_arc_0 = band_dict["band_mejora_nueva_arc"]
        band_parc_arc_0 = band_dict["band_parc_arc"]
        band_text_style = band_dict["band_text_style"]
        
        validaciones_cotas, lados_parcelas_l_f = chequeo_cotas(doc_f, parcelas_poly_close_f,medidas_dxf_f)
        
        validaciones_layout, smp_f, exp_layout_f  = chequeo_layout(doc_f,layouts,layers_mejoras_spb, band_text_style)
        
        validaciones_georref, dif_max, parc_ant_posgba_2, manz_ant_posgba_2 = georref(smp_f,parcelas_poly_close_f)
        
        zonificacion_f, cur_afectaciones_f, aph_f, band_cur_parcela_f = cur_parcela(smp_f)
        
        # validaciones_extra, area_excedente_dxf_f = resumen(parcelas_poly_close_f, lados_parcelas_l_f, excedentes_poly_f, pages_IFTAM_text, pages_IFFVN_text, pages_IFDOM_text, piso_con_mejoras_f, info_form_emp_f, info_form_nuevo_f, agip_supnueva_f, supdemo_3_f, cont_3_f, particularidades_f, medidas_dxf_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, dif_agip_f, notas_1_f, aph_f, zonificacion_f, cur_afectaciones_f, cubierta_3_f, mensura_3_f, plantas_3_f, semi_3_f, des_3_f, sup_tit_f, band_mejora_cub_arc_0, band_mejora_semi_arc_0, band_mejora_desc_arc_0, band_mejora_emp_arc_0, band_mejora_nueva_arc_0, medidas_f, band_cur_parcela_f)
        # #agregar smp_f y exp_layout_f como entrada

        if opcion.get() == 1:
            validaciones_extra, lados_iftam, smp_fomubi, exp_fomubi,area_parc_dxf, area_excedente_dxf , sup_emp_dxf_f, sup_nueva_dxf_f, plantas_dxf_f,mensura_3_f,plantas_3_f,cubierta_3_f,semi_3_f,des_3_f, cont_3_f = resumen(smp_f, pages_IFTAM_text, pages_IFFVN_text, pages_IFDOM_text,pages_FOMUBI_text,parcelas_poly,excedentes_poly,piso_con_mejoras_f, info_form_emp_f,info_form_nuevo_f,exp_layout_f, band_parc_arc_0, medidas_dxf_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_descont_dxf_f, band_mejora_cub_arc_0, band_mejora_semi_arc_0, band_mejora_desc_arc_0, band_mejora_emp_arc_0, band_mejora_nueva_arc_0,nom_parc_list)
        elif opcion.get() ==2:
            validaciones_extra, lados_iftam, smp_fomubi, exp_fomubi,area_parc_dxf, area_excedente_dxf , sup_emp_dxf_f, sup_nueva_dxf_f, plantas_dxf_f,mensura_3_f,plantas_3_f,cubierta_3_f,semi_3_f,des_3_f, cont_3_f = resumen_legajo(smp_f, pages_IFTAM_text, pages_IFFVN_text, pages_IFDOM_text,parcelas_poly,excedentes_poly,piso_con_mejoras_f, info_form_emp_f,info_form_nuevo_f,exp_layout_f, band_parc_arc_0, medidas_dxf_f, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_descont_dxf_f, band_mejora_cub_arc_0, band_mejora_semi_arc_0, band_mejora_desc_arc_0, band_mejora_emp_arc_0, band_mejora_nueva_arc_0,nom_parc_list)

        else:
            pass


        validaciones2 = concat([validaciones_archivo, validaciones_layer, validaciones_bloques, validaciones_model, validaciones_cotas, validaciones_layout, validaciones_georref, validaciones_extra], ignore_index=True)


        for i in range(len(validaciones2)):
            if "error" in (validaciones2.loc[i,'Observacion'].lower()):
                filas_con_error.append(i)
            else:
                pass

        for j in range (1,46):
            if j in filas_con_error:
                band_filas_error.append("-1")
            else:
                pass

        if "-1" in band_filas_error:
            resultado_final = "Error: Requisitos Mínimos de Admisibilidad Incorrectos"
        else:
            resultado_final = "Ok: Requisitos Mínimos de Admisibilidad Correctos"

        return validaciones2
    
    else:
        print(messagebox.showerror(message="Antes de procesar debe cargar el archivo DXF", title="Error"))
        