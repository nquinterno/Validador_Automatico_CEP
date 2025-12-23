import ezdxf
from ezdxf.math import is_point_in_polygon_2d, Vec2
from pandas import DataFrame
# from procesamiento.catastroBox import rumbo, medidaLadoPol, sup_polilinea, discretizar_curva, polig_dentro_polig
import re
# import difflib
# from json import loads
# from requests import get
# from geopandas import GeoSeries
# from shapely import Polygon, union, difference, area, geometry, Point
# from tkinter import*
# from tkinter import messagebox, filedialog, ttk


def chequeo_layout_mens(doc, layouts, layers_mejoras_spb, band_text_style):

    validaciones_layouts = DataFrame()
    
    smp = list()

    patron_layout_cep = ""
    band_pat_layout = list()
    band_muro_frozen = list()
    band_sup_frozen = list()
    band_numero_frozen = list()
    band_num_model = list()
    band_muro_frozen_dict = dict()
    band_numero_frozen_dict = dict()
    band_sup_frozen_dict= dict()
    band_num_lay_dict = dict()
    band_text_style_dict = dict()
    band_limits_dict = dict ()

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
        validaciones_layouts.loc[0,'Observacion']="Error: El/los layouts de la/s Ficha/s catastral/es no posee/n el nombre de la nomenclatura catastral de la/s parcela/s s-m-p(ej: 003-024A-007b)"
        validaciones_layouts.loc[0,'Cetegoría']='Layout'

    else:
        validaciones_layouts.loc[0,'Resultado']=0 # si hay un -1 en la bandera arroja error 
        validaciones_layouts.loc[0,'Observacion']="OK: El/los Layout/s de la/S Ficha/s catastral/es posee/n el nombre SSS-MMMM-PPPP correctamente"
        validaciones_layouts.loc[0,'Cetegoría']='Layout'

    band_entidades_limites_smp = list()


    #detecta los laypouts que no son model ni ficha catastral


    if len(smp)>0:

        for i in range(len(smp)): 
            clave = f"Ficha {smp}"
            viewport_smp = (doc.paperspace(f"{smp[i]}")).query("VIEWPORT") #consulta los viewports del layout smp, siempre agrega un elemento primero que creo que corresponde al model, hay que eliminarlo de la lista

            viewport_smp = viewport_smp[1:] #elimina el primer objeto que siempre corresponde al model

            #resetea las listas con cada smp para que los errores acumulados en cada smp sean realmente de ese smp
            band_muro_frozen = list()
            band_numero_frozen = list()
            band_sup_frozen = list()
            band_text_style = list()

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
            
            band_muro_frozen_dict[clave] = band_muro_frozen
            band_numero_frozen_dict[clave] = band_numero_frozen
            band_sup_frozen_dict[clave] = band_sup_frozen

            #Busca Números de puerta en el layout y tira error  
            
            layout_smp = doc.paperspace(f"{smp[i]}")
            num_lay = layout_smp.query("MTEXT").filter(lambda e: "N°" in e.text) | layout_smp.query("TEXT").filter(lambda e: "N°" in e.dxf.text)
            
            if len(num_lay)>0:
                band_num_lay_dict[clave] = "-1"
            else:
                band_num_lay_dict[clave]  = "0"

            #verifica que todos los textos de los layouts de ficha catastral sean Arial
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
            band_text_style_dict[clave] = band_text_style
           
            
            # inicio valida que no haya entidades fuera del paper


            # --- límites y tamaño del layout ---
            lim_lay_smp = layout_smp.get_paper_limits()
            x0, y0 = lim_lay_smp[0][0], lim_lay_smp[0][1]
            x1, y1 = lim_lay_smp[1][0], lim_lay_smp[1][1]
            xmin, xmax = (x0, x1) if x0 <= x1 else (x1, x0)
            ymin, ymax = (y0, y1) if y0 <= y1 else (y1, y0)
            tol = 1e-6  # ajustá a tus unidades

            lay_long = abs(x1 - x0)
            lay_alt  = abs(y1 - y0)

            # valida tamaños aceptando mm, cm o m (según tus casos)
            if (abs(lay_long - 0.17) < 0.001 and abs(lay_alt - 0.17) < 0.001) or \
            (abs(lay_long - 17)   < 0.1   or  abs(lay_alt - 17)   < 0.1)   or \
            (abs(lay_long - 170)  < 1     or  abs(lay_alt - 170)  < 1):
                band_limits_dict[clave] = "0"
            else:
                band_limits_dict[clave] = "-1"

            # --- consulta de entidades en paper space ---
            lineas_smp     = layout_smp.query("LINE")
            polilineas_smp = layout_smp.query("LWPOLYLINE")
            bloques_smp    = layout_smp.query("INSERT")
            text_smp       = layout_smp.query("TEXT MTEXT")
            cotas_smp      = layout_smp.query("DIMENSION")

            # --- LINE: una bandera por línea (ambos extremos dentro) ---
            for e in lineas_smp:
                xA, yA = float(e.dxf.start[0]), float(e.dxf.start[1])
                xB, yB = float(e.dxf.end[0]),   float(e.dxf.end[1])
                inA = (xmin - tol) <= xA <= (xmax + tol) and (ymin - tol) <= yA <= (ymax + tol)
                inB = (xmin - tol) <= xB <= (xmax + tol) and (ymin - tol) <= yB <= (ymax + tol)
                band_entidades_limites_smp.append("0" if (inA and inB) else "-1")

            # --- LWPOLYLINE: una bandera por polilínea (todos los vértices dentro) ---
            for e in polilineas_smp:
                ok = True
                for x, y, *_ in e.get_points("xy"):
                    x, y = float(x), float(y)
                    if not ((xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)):
                        ok = False
                        break
                band_entidades_limites_smp.append("0" if ok else "-1")

            # --- INSERT / TEXT / MTEXT / DIMENSION: por punto de inserción/definición ---
            # (si falta el punto, marca -1; ajustá si preferís saltear)
            for e in bloques_smp:
                ins = getattr(e.dxf, "insert", None)
                if ins is None:
                    band_entidades_limites_smp.append("-1")
                else:
                    x, y = float(ins[0]), float(ins[1])
                    inside = (xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)
                    band_entidades_limites_smp.append("0" if inside else "-1")

            for e in text_smp:
                ins = getattr(e.dxf, "insert", None)
                if ins is None:
                    band_entidades_limites_smp.append("-1")
                else:
                    x, y = float(ins[0]), float(ins[1])
                    inside = (xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)
                    band_entidades_limites_smp.append("0" if inside else "-1")

            for e in cotas_smp:
                # DIMENSION suele tener defpoint; si no, intentamos insert/text_midpoint
                base = getattr(e.dxf, "defpoint", None)
                if base is None:
                    base = getattr(e.dxf, "insert", None)
                if base is None:
                    base = getattr(e.dxf, "text_midpoint", None)
                if base is None:
                    band_entidades_limites_smp.append("-1")
                else:
                    x, y = float(base[0]), float(base[1])
                    inside = (xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)
                    band_entidades_limites_smp.append("0" if inside else "-1")


            # Fin valida que no haya entidades fuera del paper


        if "-1" in band_muro_frozen_dict.values():
            validaciones_layouts.loc[1,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[1,'Observacion']="Error: El layer 10-M-MURO-SEPARATIVO-PARC no se encuentra frizado algun layout de ficha catastral"
            validaciones_layouts.loc[1,'Cetegoría']='Layout'

        else:
            validaciones_layouts.loc[1,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[1,'Observacion']="Ok: El layer 10-M-MURO-SEPARATIVO-PARC se encuentra frizado en el/los layout/s de ficha catastral"
            validaciones_layouts.loc[1,'Cetegoría']='Layout'

        if "-1" in band_sup_frozen_dict.values():
            validaciones_layouts.loc[2,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[2,'Observacion']="Error: Algun layer de Sup. (excluido el de PB) no se encuentra frizado en algun layout de ficha catastral"
            validaciones_layouts.loc[2,'Cetegoría']='Layout'

        else:
            validaciones_layouts.loc[2,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[2,'Observacion']="Ok: Los layers de Sup. (excluido el de PB) se encuentran frizados en el/los layout/s de ficha catastral"
            validaciones_layouts.loc[2,'Cetegoría']='Layout'

        if "-1" in band_numero_frozen_dict.values():
            validaciones_layouts.loc[3,'Resultado']=-1 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[3,'Observacion']="Error: El Layer '06-M-NUMERO-DE-PUERTA' no se encuentra frizado en algún layout de ficha catastral"
            validaciones_layouts.loc[3,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[3,'Resultado']=0 # si hay un -1 en la bandera arroja error 
            validaciones_layouts.loc[3,'Observacion']="Ok: El Layer '06-M-NUMERO-DE-PUERTA' se encuentra frizado en el/los layout/s de ficha catastral"
            validaciones_layouts.loc[3,'Cetegoría']='Layout'

  

        if "-1" in band_limits_dict.values():
            validaciones_layouts.loc[4,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[4,'Observacion']="ERROR: El layout con nombre smp debe medir 17 x 17cm"
            validaciones_layouts.loc[4,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[4,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[4,'Observacion']="OK: El layout con nombre smp mide 17 x 17cm"
            validaciones_layouts.loc[4,'Cetegoría']='Layout'

        if "-1" in band_text_style_dict.values():
            validaciones_layouts.loc[5,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[5,'Observacion']="Error: Existen textos en el Layout o model cuya fuente es dinstinta de Arial"
            validaciones_layouts.loc[5,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[5,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[5,'Observacion']="OK: La fuente de los textos del model y layout es Arial"
            validaciones_layouts.loc[5,'Cetegoría']='Layout'

        if "-1" in band_num_lay_dict.values():
            validaciones_layouts.loc[6,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[6,'Observacion']="ERROR: Los N° de puerta solo pueden representarse en el model, layer '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[6,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[6,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[6,'Observacion']="OK: No hay N° de puerta representados en el layout"
            validaciones_layouts.loc[6,'Cetegoría']='Layout'

        if "-1" in band_num_model:
            validaciones_layouts.loc[7,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[7,'Observacion']="ERROR: Los N° de puerta solo pueden representarse en el model, layer '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[7,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[7,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[7,'Observacion']="OK: No hay N° de puerta representados en layer distinto a '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[7,'Cetegoría']='Layout'

        if "-1" in band_entidades_limites_smp:
            validaciones_layouts.loc[8,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[8,'Observacion']="ERROR: Existen entidades en el layout de ficha catastral fuera de los limites del area de impresión"
            validaciones_layouts.loc[8,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[8,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[8,'Observacion']="OK: Las entidades del layout de ficha catastral se encuentran dentro de los limites del area de impresión"
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
        validaciones_layouts.loc[4,'Observacion']="Error: No se pude validar tamaño de layout por existir mas de un layout con el formato sss-mmm-ppp"
        validaciones_layouts.loc[4,'Cetegoría']='Layout'

        validaciones_layouts.loc[5,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
        validaciones_layouts.loc[5,'Observacion']="Error: No se puede validar los estilos de texto del layout por no existir uno con el formato sss-mmm-ppp"
        validaciones_layouts.loc[5,'Cetegoría']='Layout'

        validaciones_layouts.loc[6,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
        validaciones_layouts.loc[6,'Observacion']="Error: No se puede validar N° de puerta en layout por no existir uno con el formato sss-mmm-ppp"
        validaciones_layouts.loc[6,'Cetegoría']='Layout'

        if "-1" in band_num_model:
            validaciones_layouts.loc[7,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[7,'Observacion']="ERROR: Los N° de puerta solo pueden representarse en el model, layer '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[7,'Cetegoría']='Layout'
        else:
            validaciones_layouts.loc[7,'Resultado']=0 # si hay un -1 en la bandera arroja ERROR 
            validaciones_layouts.loc[7,'Observacion']="OK: No hay N° de puerta representados en layer distinto a '06-M-NUMERO-DE-PUERTA'"
            validaciones_layouts.loc[7,'Cetegoría']='Layout'

        validaciones_layouts.loc[8,'Resultado']=-1 # si hay un -1 en la bandera arroja ERROR 
        validaciones_layouts.loc[8,'Observacion']="Error: No se puede validar entidades dentro del area de impresión del layout por no existir uno con el formato sss-mmm-ppp"
        validaciones_layouts.loc[8,'Cetegoría']='Layout'

       
        #validar todos los layots excluido el del smp, que tengan entidades y luego segun la cantidad de layouts en esa condicion la caratula va a tener que tener 1/2, 2/2 etc

        
    return  validaciones_layouts, smp
    #1- FIN Validar que el layout de la ficha tenga el nombre que debe tener 
    #2- INICIO Validar que el layout tenga la medida que indica las normas
    #5- INICIO validar georreferenciación y comparacion con parcela de catrelsa 