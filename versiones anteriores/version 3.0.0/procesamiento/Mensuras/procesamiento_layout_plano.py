import ezdxf
from ezdxf.math import is_point_in_polygon_2d, Vec2
from pandas import DataFrame
# from procesamiento.catastroBox import rumbo, medidaLadoPol, sup_polilinea, discretizar_curva, polig_dentro_polig
import re

def chequeo_layout_plano(doc,smp,bloque_caratula):
    
    plano_layout = list()
    band_car_layout = list()
    band_text_style = list()
    band_entidades_limites = list()
    validaciones_layout_plano = DataFrame()

    for layout in doc.layouts:
        if layout.name == "Model":
            pass
        elif layout.name in smp:
            pass

        else:
            plano_layout.append(layout)

    for plano in plano_layout:
        caratula_layout = plano.query('INSERT[name=="CARATULA-CABA"]')
        
        if len(caratula_layout) == 1:
            band_car_layout.append('0')
        
        else:
             band_car_layout.append('-1')

                    #verifica que todos los textos de los layouts de ficha catastral sean Arial
        textos_layout = plano.query("TEXT")|plano.query("MTEXT")
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


        # --- límites y tamaño del layout ---
            lim_lay_smp = plano.get_paper_limits()
            x0, y0 = lim_lay_smp[0][0], lim_lay_smp[0][1]
            x1, y1 = lim_lay_smp[1][0], lim_lay_smp[1][1]
            xmin, xmax = (x0, x1) if x0 <= x1 else (x1, x0)
            ymin, ymax = (y0, y1) if y0 <= y1 else (y1, y0)
            tol = 1e-6  # ajustá a tus unidades

            lay_long = abs(x1 - x0)
            lay_alt  = abs(y1 - y0)

            # # valida tamaños aceptando mm, cm o m (según tus casos)
            # if (abs(lay_long - 0.17) < 0.001 and abs(lay_alt - 0.17) < 0.001) or \
            # (abs(lay_long - 17)   < 0.1   or  abs(lay_alt - 17)   < 0.1)   or \
            # (abs(lay_long - 170)  < 1     or  abs(lay_alt - 170)  < 1):
            #     band_limits_dict[clave] = "0"
            # else:
            #     band_limits_dict[clave] = "-1"




            #validar el tamaño del layout plano con los tamaños reglamentarios





            # --- consulta de entidades en paper space ---
            lineas_smp     = plano.query("LINE")
            polilineas_smp = plano.query("LWPOLYLINE")
            bloques_smp    = plano.query("INSERT")
            text_smp       = plano.query("TEXT MTEXT")
            cotas_smp      = plano.query("DIMENSION")

            
            # --- LINE: una bandera por línea (ambos extremos dentro) ---
            for e in lineas_smp:
                xA, yA = float(e.dxf.start[0]), float(e.dxf.start[1])
                xB, yB = float(e.dxf.end[0]),   float(e.dxf.end[1])
                inA = (xmin - tol) <= xA <= (xmax + tol) and (ymin - tol) <= yA <= (ymax + tol)
                inB = (xmin - tol) <= xB <= (xmax + tol) and (ymin - tol) <= yB <= (ymax + tol)
                band_entidades_limites.append("0" if (inA and inB) else "-1")

            
            # --- LWPOLYLINE: una bandera por polilínea (todos los vértices dentro) ---
            for e in polilineas_smp:
                ok = True
                for x, y, *_ in e.get_points("xy"):
                    x, y = float(x), float(y)
                    if not ((xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)):
                        ok = False
                        break
                band_entidades_limites.append("0" if ok else "-1")

            
            # --- INSERT / TEXT / MTEXT / DIMENSION: por punto de inserción/definición ---
            # (si falta el punto, marca -1; ajustá si preferís saltear)
            for e in bloques_smp:
                ins = getattr(e.dxf, "insert", None)
                if ins is None:
                    band_entidades_limites.append("-1")
                else:
                    x, y = float(ins[0]), float(ins[1])
                    inside = (xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)
                    band_entidades_limites.append("0" if inside else "-1")

            for e in text_smp:
                ins = getattr(e.dxf, "insert", None)
                if ins is None:
                    band_entidades_limites.append("-1")
                else:
                    x, y = float(ins[0]), float(ins[1])
                    inside = (xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)
                    band_entidades_limites.append("0" if inside else "-1")

            
            for e in cotas_smp:
                # DIMENSION suele tener defpoint; si no, intentamos insert/text_midpoint
                base = getattr(e.dxf, "defpoint", None)
                if base is None:
                    base = getattr(e.dxf, "insert", None)
                if base is None:
                    base = getattr(e.dxf, "text_midpoint", None)
                if base is None:
                    band_entidades_limites.append("-1")
                else:
                    x, y = float(base[0]), float(base[1])
                    inside = (xmin - tol) <= x <= (xmax + tol) and (ymin - tol) <= y <= (ymax + tol)
                    band_entidades_limites.append("0" if inside else "-1")


    if "-1" in band_car_layout:
        validaciones_layout_plano.loc[0,'Resultado']=-1
        validaciones_layout_plano.loc[0,'Observacion']='ERROR: Cada layout de plano debe tener su caratula inserta, verifique las caratulas o elimine los layouts innecesarios'
        validaciones_layout_plano.loc[0,'Cetegoría']='Plano'
    else:
        validaciones_layout_plano.loc[0,'Resultado']=0
        validaciones_layout_plano.loc[0,'Observacion']='OK: Hay coincidencia entre los layouts de plano y las caratulas insertas'
        validaciones_layout_plano.loc[0,'Cetegoría']='Plano'

    if "-1" in band_text_style:
        validaciones_layout_plano.loc[1,'Resultado']=-1
        validaciones_layout_plano.loc[1,'Observacion']='ERROR: La fuente de los textos del layout NO es Arial'
        validaciones_layout_plano.loc[1,'Cetegoría']='Plano'
    else:
        validaciones_layout_plano.loc[1,'Resultado']=0
        validaciones_layout_plano.loc[1,'Observacion']="OK: La fuente de los textos del layout es Arial"
        validaciones_layout_plano.loc[1,'Cetegoría']='Plano'

    if "-1" in band_entidades_limites:
        validaciones_layout_plano.loc[1,'Resultado']=-1
        validaciones_layout_plano.loc[1,'Observacion']='ERROR: Existen entidades fuera de los limites de impresión en algun Layout del plano'
        validaciones_layout_plano.loc[1,'Cetegoría']='Plano'
    else:
        validaciones_layout_plano.loc[1,'Resultado']=0
        validaciones_layout_plano.loc[1,'Observacion']="OK: No hay entidades fuera de los límites de impresión en el/los Layout/s del plano"
        validaciones_layout_plano.loc[1,'Cetegoría']='Plano'

    return validaciones_layout_plano



            # Fin valida que no haya entidades fuera del paper