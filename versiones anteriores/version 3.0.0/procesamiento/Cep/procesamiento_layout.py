import ezdxf
from ezdxf.math import is_point_in_polygon_2d, Vec2
from pandas import DataFrame, read_excel, read_csv
from procesamiento.General.catastroBox import rumbo, medidaLadoPol, sup_polilinea, discretizar_curva, polig_dentro_polig
import re
import difflib
from json import loads
from requests import get
from geopandas import GeoSeries
from shapely import Polygon, union, difference, area, geometry, Point
from tkinter import*
from tkinter import messagebox, filedialog, ttk


def chequeo_layout(doc, layouts, layers_mejoras_spb, band_text_style):

    validaciones_layouts = DataFrame()
    
    smp = list()

    patron_layout_cep = ""
    band_pat_layout = list()
    band_muro_frozen = list()
    band_sup_frozen = list()
    band_numero_frozen = list()
    ban_exp = list()
    band_num_model = list()
    año_exp = ""
    n_exp = ""

    #1- INICIO Validar que el layout de la ficha tenga el nombre que debe tener
    patron_layout_cep = re.compile('(^([0-9]{3})-(([0-9]{3})|([0-9]{3}[A-Z]{1})|([0-9]{3}[Ñ]{1})|([0-9]{2}[L]{2}))-(([0-9]{3})|([0-9]{3}[a-z]{1})|(000[A-Z]{1})|([0-9]{3}[ñ]{1})|([0-9]{2}[l]{2})))$')
    
    num_model = doc.modelspace().query("MTEXT").filter(lambda e: "N°" in e.text) | doc.modelspace().query("TEXT").filter(lambda e: "N°" in e.dxf.text)

    if len(num_model)>0:
        for num in num_model:
            if num.dxf.layer != "06-M-NUMERO-DE-PUERTA":
                band_num_model.append("-1")
            else:
                band_num_model.append("0")
    else:
        band_num_model.append("0")

    for layout in layouts:


        if (patron_layout_cep.match(layout)):
            smp.append(layout)
        else:
            pass

        band_pat_layout.append(patron_layout_cep.match(layout))


    if all(v is None for v in (band_pat_layout)):
        validaciones_layouts.loc[0,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[0,'Observacion']="Error: El layout de la Ficha catastral no posee el nombre de la nomencltura catastral de la parcela s-m-p(ej: 003-024A-007b)"
        validaciones_layouts.loc[0,'Cetegoría']='Layout'

    else:
        validaciones_layouts.loc[0,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[0,'Observacion']="OK: El Layout de la Ficha catastral posee el nombre SSS-MMMM-PPPP correctamente"
        validaciones_layouts.loc[0,'Cetegoría']='Layout'


    if len(smp)==1:
        
        viewport_smp = (doc.paperspace(f"{smp[0]}")).query("VIEWPORT") #consulta los viewports del layout smp, siempre agrega un elemento primero que creo que corresponde al model, hay que eliminarlo de la lista

        viewport_smp = viewport_smp[1:] #elimina el primer objeto que siempre corresponde al model

        for viewport in viewport_smp:
            if viewport.is_frozen("10-M-MURO-SEPARATIVO-PARC"): #consulta si para el viewport el layer mencionado esta frizado o no
                band_muro_frozen.append("0")
            else:
                band_muro_frozen.append("-1")
            if viewport.is_frozen("06-M-NUMERO-DE-PUERTA"):
                band_numero_frozen.append("0")
            else:
                band_numero_frozen.append("-1")

            for layer in layers_mejoras_spb:
                if viewport.is_frozen(f"{layer}"):
                    band_sup_frozen.append("0")
                else:
                    band_sup_frozen.append("-1")
               

        if "-1" in band_muro_frozen:
            validaciones_layouts.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[1,'Observacion']="Error: El layer 10-M-MURO-SEPARATIVO-PARC no se encuentra frizado en el layout de la ficha catastral"
            validaciones_layouts.loc[1,'Cetegoría']='Layout'

        else:
            validaciones_layouts.loc[1,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[1,'Observacion']="Ok: El layer 10-M-MURO-SEPARATIVO-PARC se encuentra frizado en el layout de la ficha catastral"
            validaciones_layouts.loc[1,'Cetegoría']='Layout'

        if "-1" in band_sup_frozen:
            validaciones_layouts.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[2,'Observacion']="Error: Algun layer de Sup. (excluido el de PB) no se encuentra frizado en el layout de la ficha catastral"
            validaciones_layouts.loc[2,'Cetegoría']='Layout'

        else:
            validaciones_layouts.loc[2,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[2,'Observacion']="Ok: Los layers de Sup. (excluido el de PB) se encuentran frizados en el layout de la ficha catastral"
            validaciones_layouts.loc[2,'Cetegoría']='Layout'

        if "-1" in band_numero_frozen:
            validaciones_layouts.loc[3,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[3,'Observacion']="Error: El Layer '06-M-NUMERO-DE-PUERTA' no se encuentra frizado en el viewport de la ficha catastral"
            validaciones_layouts.loc[3,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[3,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[3,'Observacion']="Ok: El Layer '06-M-NUMERO-DE-PUERTA' se encuentra frizado en el viewport de la ficha catastral"
            validaciones_layouts.loc[3,'Cetegoría']='Layout'


        layout_smp = doc.paperspace(f"{smp[0]}")
        
        # busca numero de expediente insertado como bloque
        bloque_exp = layout_smp.query('INSERT[name=="expediente"]')
        # busca numero de expediente insertado como texto
        #text_exp = layout_smp.query("MTEXT|TEXT").filter(lambda e: "EX-" in e.text or "-GCABA-DGROC" in e.text)
        text_exp = layout_smp.query("MTEXT").filter(lambda e: "EX-" in e.text or "-GCABA-DGROC" in e.text)| layout_smp.query("TEXT").filter(lambda e: "EX-" in e.dxf.text or "-GCABA-DGROC" in e.dxf.text)
        text=""

        #Busca Números de puerta en el layout y tira error  
        num_lay = layout_smp.query("MTEXT").filter(lambda e: "N°" in e.text) | layout_smp.query("TEXT").filter(lambda e: "N°" in e.dxf.text)
        
        if len(num_lay)>0:
            band_num_lay = "-1"
        else:
            band_num_lay = "0"

        #Busca si hay numeros de peurta en el model en un layer que no sea el de numero de puerta y tira error

        textos_layout = layout_smp.query("TEXT")|layout_smp.query("MTEXT")
        estilos = doc.styles
        for text in textos_layout:
            if text.dxf.style in estilos:
                style = estilos.get(text.dxf.style)
                if style.dxf.font != "arial.ttf":
                    band_text_style.append("-1")
                else:
                    band_text_style.append("0")
            else:
                pass
        
        
        if len(bloque_exp)==1:
            band_bloque_exp = "0"
            for bloque in (bloque_exp):
                for attrib in bloque.attribs:
                    if attrib.dxf.tag=="AÑO":
                        año_exp = attrib.dxf.text
                        if attrib.dxf.text == None:
                            ban_exp.append(-1)
                        else:
                            ban_exp.append(0)

                    elif attrib.dxf.tag=="NRO":
                        n_exp = attrib.dxf.text
                        if attrib.dxf.text == None:
                            ban_exp.append(-1)
                        else:
                            ban_exp.append(0)
                    else:
                        ban_exp.append(-2)

            if -1 in ban_exp:
                validaciones_layouts.loc[4,'Resultado']=50
                validaciones_layouts.loc[4,'Observacion']='Verificar: El bloque "expediente" tiene campos vacíos'
                validaciones_layouts.loc[4,'Cetegoría']='Bloques'
            
            elif -2 in ban_exp:
                validaciones_layouts.loc[4,'Resultado']=50
                validaciones_layouts.loc[4,'Observacion']='Verificar: Se ha modificado la configuración del bloque "expediente"'
                validaciones_layouts.loc[4,'Cetegoría']='Bloques'

            else:
                validaciones_layouts.loc[4,'Resultado']=0
                validaciones_layouts.loc[4,'Observacion']='Ok: El bloque "expediente" tiene campos completos'
                validaciones_layouts.loc[4,'Cetegoría']='Bloques' 

            exp_layout = "EX-" + año_exp +"-"+ n_exp + "- -GCABA-DGROC"

        elif len(bloque_exp)>1:
            band_bloque_exp = "-2"
            if len(text_exp)==1:
                for entitie in text_exp:
                    text = entitie.dxf.text

                patron_ex = r'EX-(.{13})'
                resultado = re.search(patron_ex, text)

                if resultado:
                    exp_layout = resultado.group()
                else:
                    exp_layout = "EX-" + año_exp +"-"+ n_exp + "- -GCABA-DGROC"
                band_tex_exp = "0"

            elif len(text_exp)>1:
                band_tex_exp = "-2"
                for text in text_exp:
                    if "EX-" in text.dxf.text:
                        exp_layout = text.dxf.text
                    else:
                        pass
            else:
                exp_layout = "EX-" + año_exp +"-"+ n_exp + "- -GCABA-DGROC"
                band_tex_exp = "-1"

            validaciones_layouts.loc[4,'Resultado']=50
            validaciones_layouts.loc[4,'Observacion']=f'Verificar: Se ha insertado más de un bloque "expediente" en el layout {smp[0]} '
            validaciones_layouts.loc[4,'Cetegoría']='Bloques'

        else:
            if len(text_exp)==1:
                for entitie in text_exp:
                    text = entitie.dxf.text
                patron_ex = r'EX-(.{13})'
                resultado = re.search(patron_ex, text)

                if resultado:
                    exp_layout = resultado.group()
                else:
                    exp_layout = "EX-" + año_exp +"-"+ n_exp + "- -GCABA-DGROC"
                band_tex_exp = "0"

            elif len(text_exp)>1:
                band_tex_exp = "-2"
                for text in text_exp:
                    if "EX-" in text.dxf.text:
                        exp_layout = text.dxf.text
                    else:
                        pass
            else:
                exp_layout = "EX-" + "" + "" + "- -GCABA-DGROC"
                band_tex_exp = "-1"
            validaciones_layouts.loc[4,'Resultado']=50
            validaciones_layouts.loc[4,'Observacion']=f'Verificar: No se ha insertado el bloque "expediente" en el layout {smp[0]}'
            validaciones_layouts.loc[4,'Cetegoría']='Bloques'

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
            validaciones_layouts.loc[5,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[5,'Observacion']="ERROR: El layout con nombre smp debe medir 17 x 17cm"
            validaciones_layouts.loc[5,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[5,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[5,'Observacion']="OK: El layout con nombre smp mide 17 x 17cm"
            validaciones_layouts.loc[5,'Cetegoría']='Layout'

        if "-1" in band_text_style:
            validaciones_layouts.loc[6,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[6,'Observacion']="Error: Existen textos en el Layout o model cuya fuente es dinstinta de Arial"
            validaciones_layouts.loc[6,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[6,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[6,'Observacion']="OK: La fuente de los textos del model y layout es Arial"
            validaciones_layouts.loc[6,'Cetegoría']='Layout'

        if "-1" in band_num_lay:
            validaciones_layouts.loc[7,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[7,'Observacion']="ERROR: Los N° de puerta solo pueden representarse en el model, layer '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[7,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[7,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[7,'Observacion']="OK: No hay N° de puerta representados en el layout"
            validaciones_layouts.loc[7,'Cetegoría']='Layout'

        if "-1" in band_num_model:
            validaciones_layouts.loc[8,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[8,'Observacion']="ERROR: Los N° de puerta solo pueden representarse en el model, layer '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[8,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[8,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[8,'Observacion']="OK: No hay N° de puerta representados en layer distinto a '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[8,'Cetegoría']='Layout'
    else:
        validaciones_layouts.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[1,'Observacion']= "Error: No se puden validar los layers frizados por existir mas de un layout con el formato sss-mmm-ppp"
        validaciones_layouts.loc[1,'Cetegoría']='Layout'

        validaciones_layouts.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[2,'Observacion']= "Error: No se puden validar los layers frizados por existir mas de un layout con el formato sss-mmm-ppp"
        validaciones_layouts.loc[2,'Cetegoría']='Layout'

        validaciones_layouts.loc[3,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[3,'Observacion']="Error: No se puden vaidar los layers frizados por existir mas de un layout con el formato sss-mmm-ppp"
        validaciones_layouts.loc[3,'Cetegoría']='Layout'

        validaciones_layouts.loc[4,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[4,'Observacion']="Error: No se pude validar el bloque 'expediente' por existir mas de un layout con el formato sss-mmm-ppp"
        validaciones_layouts.loc[4,'Cetegoría']='Layout'

        validaciones_layouts.loc[5,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[5,'Observacion']="Error: No se pude validar tamaño de layout por existir mas de un layout con el formato sss-mmm-ppp"
        validaciones_layouts.loc[5,'Cetegoría']='Layout'

        validaciones_layouts.loc[6,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
        validaciones_layouts.loc[6,'Observacion']="Error: No se puede validar los estilos de texto del layout por no existir uno con el formato sss-mmm-ppp"
        validaciones_layouts.loc[6,'Cetegoría']='Layout'

        validaciones_layouts.loc[7,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
        validaciones_layouts.loc[7,'Observacion']="Error: No se puede validar N° de puerta en layout por no existir uno con el formato sss-mmm-ppp"
        validaciones_layouts.loc[7,'Cetegoría']='Layout'

        if "-1" in band_num_model:
            validaciones_layouts.loc[8,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[8,'Observacion']="ERROR: Los N° de puerta solo pueden representarse en el model, layer '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[8,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[8,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[8,'Observacion']="OK: No hay N° de puerta representados en layer distinto a '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[8,'Cetegoría']='Layout'

        exp_layout = "EX-" + año_exp +"-"+ n_exp + "- -GCABA-DGROC"

        #validar todos los layots excluido el del smp, que tengan entidades y luego segun la cantidad de layouts en esa condicion la caratula va a tener que tener 1/2, 2/2 etc

    


        
    return  validaciones_layouts, smp, exp_layout
    #1- FIN Validar que el layout de la ficha tenga el nombre que debe tener 
    #2- INICIO Validar que el layout tenga la medida que indica las normas
    #5- INICIO validar georreferenciación y comparacion con parcela de catrelsa 