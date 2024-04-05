import math
import ezdxf
from ezdxf.math.construct2d import is_point_in_polygon_2d, Vec2

def midPointArc(arc):
    #parametros del arco
    try:
        start_angle = math.radians(arc.dxf.start_angle)
        end_angle = math.radians(arc.dxf.end_angle)
        centro = arc.dxf.center
        radio =  arc.dxf.radius
    except:
        start_angle = math.radians(arc.start_angle)
        end_angle = math.radians(arc.end_angle)
        centro = arc.center
        radio =  arc.radius

    start_point = arc.start_point
    end_point = arc.end_point
    angle = abs(end_angle - start_angle)


    dx = start_point[0] - centro[0]
    dy = start_point[1] - centro[1]
    
    rotated_dx = (dx * math.cos(angle/2) - dy * math.sin(angle/2)) + centro[0]
    rotated_dy = (dx * math.sin(angle/2) + dy * math.cos(angle/2)) + centro[1]
    
    dx_1 = end_point[0] - centro[0]
    dy_1 = end_point[1] - centro[1]
    
    rotated_dx_1 = (dx_1 * math.cos(angle/2) - dy_1 * math.sin(angle/2)) + centro[0]
    rotated_dy_1 = (dx_1 * math.sin(angle/2) + dy_1 * math.cos(angle/2)) + centro[1]

    midpoint_arc_1 = (rotated_dx, rotated_dy)
    midpoint_arc_2 = (rotated_dx_1, rotated_dy_1)
    
    #calcula los angulos del pto star, end del arco y de los dos sospechosos a midpoint del arco, el que tenga angulo que se encuentre entre el start y el end es el verdadero punto medio, y ese usamos para ver si esta adentro o fuera d ela polilinea para saber si restamos la sup del arco o la sumamos.

    angle_end_point = math.atan2(end_point[1]- centro[1], end_point[0] - centro [0])
    angle_start_point = math.atan2(start_point[1]- centro[1], start_point[0] - centro [0])
    angle_midpoint_arc_1= math.atan2(dy, dx)
    angle_midpoint_arc_2= math.atan2(dy_1, dx_1)
    
    dif_angle_1 = angle_midpoint_arc_1 - (angle_end_point + angle_start_point)/2
    dif_angle_2 = angle_midpoint_arc_2 - (angle_end_point + angle_start_point)/2

    dif_start_mid_1 = round(math.sqrt((midpoint_arc_1[0] - start_point[0])**2 + (midpoint_arc_1[1] - start_point[1])**2),2)
    dif_start_mid_2 = round(math.sqrt((midpoint_arc_2[0] - start_point[0])**2 + (midpoint_arc_2[1] - start_point[1])**2),2)
    dif_end_mid_1 = round(math.sqrt((midpoint_arc_1[0] - end_point[0])**2 + (midpoint_arc_1[1] - end_point[1])**2),2)
    dif_end_mid_2 = round(math.sqrt((midpoint_arc_2[0] - end_point[0])**2 + (midpoint_arc_2[1] - end_point[1])**2),2)

    
    if abs(dif_start_mid_1) == abs(dif_end_mid_1):
        
        pto_arc = Vec2(midpoint_arc_1[0],midpoint_arc_1[1])
        
    elif abs(dif_start_mid_2) == abs(dif_end_mid_2):
        
        pto_arc = Vec2(midpoint_arc_2[0],midpoint_arc_2[1])

    else:
        pto_arc = [0,0]

    return pto_arc

def sup_polilinea(parcela):
    band_parc_arc_1 = list()
    sup_arc_parc = list()
    sup_arco = list()
    
    if parcela.has_arc:
        vertices_p1 = list()
        
        for vert in parcela.vertices():
            if vert in vertices_p1:
                pass
            else:
                vertices_p1.append(vert)
        
        vertices_p2 = Vec2.list(vertices_p1)
        vertices_p3 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=-0.01, closed=True))
        vertices_p4 = list(ezdxf.math.offset_vertices_2d(vertices_p2,offset=0.01, closed=True))
        band_parc_arc_1.append("1")
        segmentos = parcela.virtual_entities()
        
        for seg in segmentos:
            if seg.dxftype()== "ARC":
                arc = seg
                start_angle = math.radians(arc.dxf.start_angle)
                end_angle = math.radians(arc.dxf.end_angle)
                radio = arc.dxf.radius
                angle = abs(end_angle - start_angle)
                
                pto_arc = midPointArc(arc)
                #area completa de la seccion de circulo
                sup_arc_0=(((radio)**2)*(angle/2))
                
                #area del triangulo a restar dado que ya esta incluido en el calculo de la sup del poligono
                sup_arc_1 = 2 * ((radio * math.sin(angle/2)) * (radio * math.cos(angle/2)))/2
                
                #caluclo real de la superficie del arco
                sup_arco.append(sup_arc_0-sup_arc_1)
                
                if ezdxf.math.is_point_in_polygon_2d(pto_arc,vertices_p3,abs_tol=1e-3)==-1:
                    if ezdxf.math.is_point_in_polygon_2d(pto_arc,vertices_p4,abs_tol=1e-3)==-1:
                        
                        sup_arc_parc.append(round((sup_arc_0-sup_arc_1),2))
                    else:
                        
                        sup_arc_parc.append(round(-1*(sup_arc_0-sup_arc_1),2))
                else:
                    
                    sup_arc_parc.append(round(-1*(sup_arc_0-sup_arc_1),2))
            else:
                pass

        if len(sup_arc_parc):
            sup_arcos = 0
            for sup in sup_arc_parc:
                sup_arcos = sup_arcos + sup
        else:
            sup_arcos = 0


        area_parc_dxf_0 = round(ezdxf.math.area(Vec2.list(parcela.get_points('xy'))),2)
        area_parc_dxf = area_parc_dxf_0 + round(sup_arcos,2)
    else:
        band_parc_arc_1.append("0")
        area_parc_dxf = round(ezdxf.math.area(Vec2.list(parcela.get_points('xy'))),2)
    
    return area_parc_dxf

def medidaLadoPol(seg):
    if seg.dxftype()== "ARC":
        arc = seg
        start_angle = math.radians(arc.dxf.start_angle)
        end_angle = math.radians(arc.dxf.end_angle)
        radio = arc.dxf.radius
        angle = abs(end_angle - start_angle)
        medida = round(radio * angle,2)
    else:
        start = seg.dxf.start
        end = seg.dxf.end
        medida = round(math.sqrt(((start[0]-end[0])**2)+((start[1]-end[1])**2)),2)

    return medida

def rumbo(parcela, seg):
    pi = math.pi
    vertices_p1 = list()
    vertices_p0 = list()

    if parcela.has_arc:
        lados = parcela.virtual_entities()

        for lado in lados:
            if lado.dxftype() == "ARC":
                arco_discretizado = discretizar_curva(lado,0.01)
                #dar vuelta el arco para que coincida con los vertices
                if len(vertices_p0):
                    if vertices_p0[-1] == arco_discretizado[0]:
                        
                        vertices_p0 = vertices_p0 + arco_discretizado
                    elif vertices_p0[-1] == arco_discretizado[-1]:
                        
                        vertices_p0 = vertices_p0 + list(reversed(arco_discretizado))
                    else:
                        pass
                else:
                    vertices_p0 = vertices_p0 + arco_discretizado

                vertices_p0 = vertices_p0 + arco_discretizado
            else:
                lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]

                vertices_p0 = vertices_p0 + lado_recto

        for vert in vertices_p0:
            if vert in vertices_p1:
                pass
            else:
                vertices_p1.append(vert)
    else:
    
        for vert in parcela.vertices():
            if vert in vertices_p1:
                pass
            else:
                vertices_p1.append(vert)
    
    vertices_p2 = Vec2.list(vertices_p1)  
    

    if seg.dxftype()== "ARC":
        p1 = seg.start_point
        p2 = seg.end_point
        centro = seg.dxf.center
        radio = seg.dxf.radius
        p3 =  midPointArc(seg)

        #calcular el punto medio de un ofset exterior e interior
        dx = p3[0] - centro[0]
        dy = p3[1] - centro[1]
        ang_0 = math.atan2(dy,dx)
        
        if ang_0 >= 0:
            ang = ang_0
        else:
            ang = ang_0 + 2 * pi

        midpoint_seg1 = (centro[0]+(radio-0.01)*math.cos(ang),centro[1]+(radio-0.01)*math.sin(ang))
        midpoint_seg2 = (centro[0]+((radio+0.01)*math.cos(ang)),centro[1]+((radio+0.01)*math.sin(ang)))

    else:
        p1 = seg.dxf.start
        p2 = seg.dxf.end
        p3 = ((p1[0]+p2[0])/2,(p1[1]+p2[1])/2)
        
        vert_offset = Vec2.list((p1,p2))
        offset_seg_1 = list(ezdxf.math.offset_vertices_2d(vert_offset,offset=0.050, closed=False)) 
        offset_seg_2 = list(ezdxf.math.offset_vertices_2d(vert_offset,offset=-0.050, closed=False)) 

        #puntos medios de los offsets para saber cual d elos dos esta dentro de la parcela y asi descartar el rumbo que no va
        midpoint_seg1 = (((offset_seg_1[0])[0]+(offset_seg_1[1])[0])/2,((offset_seg_1[0])[1]+(offset_seg_1[1])[1])/2)

        midpoint_seg2 = (((offset_seg_2[0])[0]+(offset_seg_2[1])[0])/2,((offset_seg_2[0])[1]+(offset_seg_2[1])[1])/2)
        
    #consulta cual de los offset esta dentro de la parcela

    if ezdxf.math.is_point_in_polygon_2d(Vec2(midpoint_seg1),vertices_p2,abs_tol=1e-3)==-1:
        if ezdxf.math.is_point_in_polygon_2d(Vec2(midpoint_seg2),vertices_p2,abs_tol=1e-3)==-1:
            pass
        else:
            pto_interior = midpoint_seg2
    else:
        pto_interior = midpoint_seg1


    #calcula del segmento dx,dy, y angulo de inclinacion
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    ang_0 = math.atan2(dy,dx)
    
    #convierte el angulo a un angulo posisitvo en radianes entre 0-2pi
    if ang_0 >= 0:
        ang = ang_0
    else:
        ang = ang_0 + 2 * pi
    
    #calcula dx, dy entre punto medio del arco y punto medio del "arco con offset de 0.01" dentro del poligono

    dx_int = p3[0] - pto_interior[0]
    dy_int = p3[1] - pto_interior[1]

    #segun el angulo de inclinacion reduce las posibilidades de rumbo a solo 2 opuestas.
    if ang <= (pi/2):
        if ang <= (7/16 * pi) and ang > (5/16 * pi):
            rumbo_0 = "ONO-ESE"
            
            if dx_int>0:
                rumbo = "ESE"
            else:
                rumbo = "ONO"

        elif  ang <= (5/16 * pi) and ang > (3/16 * pi):
            rumbo_0 = "NO-SE"
            
            if dx_int>0:
                rumbo = "SE"
            else:
                rumbo = "NO"

        elif  ang <= (3/16 * pi) and ang > (1/16 * pi):
            rumbo_0 = "NNO-SSE"
            
            if dy_int>0:
                rumbo = "NNO"
            else:
                rumbo = "SSE"

        elif  ang <= (1/16 * pi):
            rumbo_0 = "N-S"
            
            if dy_int>0:
                rumbo = "N"
            else:
                rumbo = "S"

        elif ang > (7/16 * pi):
            rumbo_0 = "E-O"

            if dx_int>0:
                rumbo = "E"
            else:
                rumbo = "O"

    elif ang <= (pi):
        
        if ang <= (15/16 * pi) and ang > (13/16 * pi):
            rumbo_0 = "NNE-SSO"
            
            if dy_int>0:
                rumbo = "NNE"
            else:
                rumbo = "SSO"

        elif  ang <= (13/16 * pi) and ang > (11/16 * pi):
            rumbo_0 = "NE-SO"
            
            if dx_int>0:
                rumbo = "NE"
            else:
                rumbo = "SO"
        
        elif  ang <= (11/16 * pi) and ang > (9/16 * pi):
            rumbo_0 = "ENE-OSO"

            if dx_int>0:
                rumbo = "ENE"
            else:
                rumbo = "OSO"
        
        elif  ang <= (9/16 * pi):
            rumbo_0 = "E-O"
        
            if dx_int>0:
                rumbo = "E"
            else:
                rumbo = "O"

        elif ang > (15/16 * pi):
            rumbo_0 = "N-S"
            
            if dy_int>0:
                rumbo = "N"
            else:
                rumbo = "S"

    elif ang <= ((3/2)*(pi)):
        
        if ang <= (23/16 * pi) and ang > (21/16 * pi):
            rumbo_0 = "ONO-ESE"
            
            if dx_int>0:
                rumbo = "ESE"
            else:
                rumbo = "ONO"

        elif  ang <= (21/16 * pi) and ang > (19/16 * pi):
            rumbo_0 = "NO-SE"
            
            if dx_int>0:
                rumbo = "SE"
            else:
                rumbo = "NO"

        elif  ang <= (19/16 * pi) and ang > (17/16 * pi):
            rumbo_0 = "NNO-SSE"
            
            if dy_int>0:
                rumbo = "NNO"
            else:
                rumbo = "SSE"

        elif  ang <= (17/16 * pi):
            rumbo_0 = "N-S"
            
            if dy_int>0:
                rumbo = "N"
            else:
                rumbo = "S"

        elif ang > (23/16 * pi):
            rumbo_0 = "E-O"

            if dx_int>0:
                rumbo = "E"
            else:
                rumbo = "O"

    else:
        
        if ang <= (31/16 * pi) and ang > (29/16 * pi):
            rumbo_0 = "NNE-SSO"

            if dy_int>0:
                rumbo = "NNE"
            else:
                rumbo = "SSO"

        elif  ang <= (29/16 * pi) and ang > (27/16 * pi):
            rumbo_0 = "NE-SO"
            
            if dx_int>0:
                rumbo = "NE"
            else:
                rumbo = "SO"

        elif  ang <= (27/16 * pi) and ang > (25/16 * pi):
            rumbo_0 = "ENE-OSO"
            
            if dx_int>0:
                rumbo = "ENE"
            else:
                rumbo = "OSO"
            
        elif  ang <= (25/16 * pi):
            rumbo_0 = "E-O"

            if dx_int>0:
                rumbo = "E"
            else:
                rumbo = "O"

        elif ang > (31/16 * pi):
            rumbo_0 = "N-S"
            
            if dy_int>0:
                rumbo = "N"
            else:
                rumbo = "S"

        else:
            pass
    return rumbo

def polig_dentro_polig(polig_madre, polig_hijo, tol):
    poligono_dizcretizado_0 = list()
    poligono_dizcretizado_1 = list()
    vertices_pm = list()
    vertices_ph = list()
    
    #prepara los poligonos madre e hijo para comparar, si tiene arco algun poligono genera vertices dentro del arco para que la flecha sea menor a 0.01m

    if type(polig_madre) != list:
        if polig_madre.has_arc:
            for lado in polig_madre.virtual_entities():
                if lado.dxftype()== "ARC":
                    arco_dizcretizado = discretizar_curva(lado,0.01) #lista de vertices de un arco para discretizarlo en lineas
                    poligono_dizcretizado_0 = poligono_dizcretizado_0 + arco_dizcretizado
                else:
                    lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]
                    poligono_dizcretizado_0 = poligono_dizcretizado_0 + lado_recto

            for vert in poligono_dizcretizado_0:
                if vert in vertices_pm:
                    pass
                else:
                    vertices_pm.append(vert)

        else:

            for vert in polig_madre:
                if vert in vertices_pm:
                    pass
                else:
                    vertices_pm.append(vert)
    else:

        for vert in polig_madre:
            if vert in vertices_pm:
                pass
            else:
                vertices_pm.append(vert)

    if polig_hijo.has_arc:

        for lado in polig_hijo.virtual_entities():
            if lado.dxftype()== "ARC":
                arco_dizcretizado = discretizar_curva(lado,0.01) #lista de vertices de un arco para discretizarlo en lineas
                poligono_dizcretizado_0 = poligono_dizcretizado_0 + arco_dizcretizado
            else:
                lado_recto = [[round(lado.dxf.start.x,3),round(lado.dxf.start.y,3)],[round(lado.dxf.end.x,3),round(lado.dxf.end.y,3)]]
                poligono_dizcretizado_0 = poligono_dizcretizado_0 + lado_recto

        for vert in poligono_dizcretizado_0:
            if vert in vertices_ph:
                pass
            else:
                vertices_ph.append(vert)
    else:

        for vert in polig_hijo:
            if vert in vertices_ph:
                pass
            else:
                vertices_ph.append(vert)

    #para cada mejora obtiene los vertices y los prepara para la función de control
    # vertices_pm1 = Vec2.list(vertices_pm)
    # vertices_ph1 = Vec2.list(vertices_ph)
    vertices_pm1 = list()
    vertices_ph1 = list()


    for vert in vertices_pm:
        vertices_pm1.append(Vec2(vert[0],vert[1]))


    for vert in vertices_ph:
        vertices_ph1.append(Vec2(vert[0],vert[1]))
    
    #vertices_p1 = parcela.get_points('xy')  #para cada parcela obtiene los vertices y los prepara para la función de control

    vertices_pm2 = list(ezdxf.math.offset_vertices_2d(vertices_pm1,offset=tol*(-1), closed=True))
    vertices_pm3 = list(ezdxf.math.offset_vertices_2d(vertices_pm1,offset=tol, closed=True))
    band_vert_dentro=list() #inicia bandera que valida si los vertices de la mejora caen dentro de el polig. de parcela
    for i in range (0,len(vertices_ph1)): 
        
        if ezdxf.math.is_point_in_polygon_2d(vertices_ph1[i],vertices_pm2,abs_tol=1e-3)==-1: #validación de vertices arroja -1 si cae fuera, 0 si cae en los limites y 1 si cae dentro
            if ezdxf.math.is_point_in_polygon_2d(vertices_ph1[i],vertices_pm3,abs_tol=1e-3)==-1:
                band_vert_dentro.append('-1')
            else:
                band_vert_dentro.append('0')
        else:
            band_vert_dentro.append('0')
            
    if '-1' in band_vert_dentro: #bandera que indica si el poligono hujo esta dentro del poligono madre
        band_polig_dentro = False
    else:
        band_polig_dentro = True

    return band_polig_dentro

#--- 3 FIN EXPORTAR PDF CON RESUMEN  ---#

def discretizar_curva(arc,tol):
    # doc3= ezdxf.new()
    vert_arc = list()
    # midpoint = midPointArc(arc)

    # start_angle = math.radians(arc.dxf.start_angle)
    # end_angle = math.radians(arc.dxf.end_angle)
    start_point = arc.start_point
    end_point = arc.end_point
    # angle = abs(end_angle - start_angle)
    if arc.dxf.end_angle < 0:
        end_angle = arc.dxf.end_angle + 360
    else:
        end_angle = arc.dxf.end_angle

    if arc.dxf.start_angle < 0:
        start_angle = arc.dxf.start_angle + 360
    else:
        start_angle = arc.dxf.start_angle
    
    
    angle_0 = abs(end_angle - start_angle)
    centro = arc.dxf.center
    radio = arc.dxf.radius

    #calcular el angulo en el que debo dividir el arco para que cumpla que la flecha sea menor a una tolerancia
    arc_0 = arc
    flecha = 100
    #calcula el arco minimo arc_0 ´para que la flecha sea menor a la tolerancia, y va dividiendo en dos el arco hasta obtener el minimo
    while flecha > tol:

        midpoint_0 = midPointArc(arc_0)
        arc_nuevo = ezdxf.math.ConstructionArc.from_2p_radius(start_point, midpoint_0, radio)
        midpoint_arc = midPointArc(arc_nuevo)
        midpoint_cuerda = ((arc_nuevo.start_point[0] + arc_nuevo.end_point[0])/2, (arc_nuevo.start_point[1] + arc_nuevo.end_point[1])/2)
        flecha = math.sqrt(((midpoint_cuerda[0] - midpoint_arc[0])**2)+((midpoint_cuerda[1]-midpoint_arc[1])**2))
        arc_0 = arc_nuevo

    
    angulo_ini_0 = abs((arc_0.end_angle - arc_0.start_angle))
    num_vert = int(angle_0 / angulo_ini_0) #numero de vertices en funcion al angulo que hace que la flecha sea menor a tol
    #num_vert = int(angle_0 / angulo_ini_0)+1
    angulo_ini_1 = math.radians(angle_0 / num_vert) #angulo de cada arquito, para calcular los vertices
    angulo_ini_2 = angle_0 / num_vert
    #calcular todos los vertices del arco en base a el angulo_ini_1,  a num_vert, a 

    #probar para que lado hay que rotar los puntos
    dx_1 = start_point[0] - centro[0]
    dy_1 = start_point[1] - centro[1]

    dx_2 = end_point[0] - centro[0]
    dy_2 = end_point[1] - centro[1]


    for i in range (0,num_vert+1):

        rotated_dx_1 = (dx_1 * math.cos(angulo_ini_1 * i) - dy_1 * math.sin(angulo_ini_1 * i)) + centro[0]
        rotated_dy_1 = (dx_1 * math.sin(angulo_ini_1 * i) + dy_1 * math.cos(angulo_ini_1 * i)) + centro[1]
        
        rotated_dx_2 = (dx_2 * math.cos(angulo_ini_1 * i) - dy_2 * math.sin(angulo_ini_1 * i)) + centro[0]
        rotated_dy_2 = (dx_2 * math.sin(angulo_ini_1 * i) + dy_2 * math.cos(angulo_ini_1 * i)) + centro[1]

        dist_end = round(math.sqrt(((rotated_dx_1 - end_point[0])**2)+((rotated_dy_1 - end_point[1])**2)),2)
        dist_start = round(math.sqrt(((rotated_dx_2 - start_point[0])**2)+((rotated_dy_2 - start_point[1])**2)),2)

        if dist_end < dist_start:
            punto = [round(rotated_dx_1,3),round(rotated_dy_1,3)]
        elif dist_end > dist_start:
            punto = [round(rotated_dx_2,3),round(rotated_dy_2,3)]
        else:
            punto = [round(rotated_dx_1,3),round(rotated_dy_1,3)]  
        vert_arc.append(punto)

    return vert_arc


def correlacion_poligonos(pol_medido,pol_antec,tol):
    dist_parc_ant_0 = list()
    dist_parc_ant = list()
    for vert_parc in pol_medido:
        dist_vertp_verta = list()
        for vert_ant in pol_antec:
            dist = math.sqrt(((vert_parc[0]-vert_ant[0])**2)+((vert_parc[1]-vert_ant[1]))**2)
            dist_vertp_verta.append({"dist":dist,"vp":[vert_parc[0],vert_parc[1]],"vant":[vert_ant[0],vert_ant[1]]})
        
        # Encontrar el valor mínimo de 'dist' en la lista de diccionarios
        min_dist = min(dic['dist'] for dic in dist_vertp_verta)

        # Filtrar la lista de diccionarios basándote en el valor mínimo de 'dist'
        vert_min_dist = [dic for dic in dist_vertp_verta if dic['dist'] == min_dist]

        dist_parc_ant_0.append(vert_min_dist[0])
        dist_parc_ant = dist_parc_ant_0
    

    #recorre la lista de vertices de la parcela con sus distancias y si es mayor a una tolerancia lo guarda en una lista de vertices a chequear con el algoritmo de distancia a polilinea 
    vert_parc_chequeo = list()
    for k in dist_parc_ant:
        if float(k['dist'])>tol:
            vert_parc_chequeo.append(k["vp"])
            
        else:
            pass
            
    #calcula todas las distancias de los vertices antecedentes a los vertices de la parcela
    dist_ant_parc_0 = list()
    dist_ant_parc = list()
    for vert_ant in pol_antec:
        dist_verta_vertp = list()
        for vert_parc in pol_medido:
            dist = (math.sqrt(((vert_parc[0]-vert_ant[0])**2)+((vert_parc[1]-vert_ant[1]))**2))
            dist_verta_vertp.append({"dist":dist,"vp":[vert_parc[0],vert_parc[1]],"vant":[vert_ant[0],vert_ant[1]]})
        
        # Encontrar el valor mínimo de 'dist' en la lista de diccionarios
        min_dist = min(dic['dist'] for dic in dist_verta_vertp)

        # Filtrar la lista de diccionarios basándote en el valor mínimo de 'dist'
        vert_min_dist = [dic for dic in dist_verta_vertp if dic['dist'] == min_dist]

        dist_ant_parc_0.append(vert_min_dist[0])
        dist_ant_parc = dist_ant_parc_0
    
    #recorre la lista de vertices del antecedente con sus distancias y si es mayor a una tolerancia lo guarda en una lista de vertices a chequear con el algoritmo de distancia a polilinea 
    vert_ant_chequeo = list()
    dist_sup_tol = list()
    for k in  dist_ant_parc:

        if float(k["dist"])>tol:
            vert_ant_chequeo.append(k["vant"])
            dist_sup_tol.append(float(k["dist"]))
        else:
            pass

    if len(vert_parc_chequeo)>0:
        dist_parc_ant_2 = list()
        for vert in vert_parc_chequeo:
            print("vert")
            print(vert)
            vert_parc = Vec2.list(vert)
            dist_vpar_lant = list()
            for i in range(len(pol_antec)):
                dist = math.distance_point_line_2d(vert_parc,pol_antec[i-1], pol_antec[i])
                
                dist_vpar_lant.append({"dist":dist,"vp":[vert_parc[0],vert_parc[1]],"vant_1":[pol_antec[i-1]],"vant_2":pol_antec[i]})
            
            # Encontrar el valor mínimo de 'dist' en la lista de diccionarios
            min_dist = min(dic['dist'] for dic in dist_vpar_lant)

            # Filtrar la lista de diccionarios basándote en el valor mínimo de 'dist'
            vert_min_dist = [dic for dic in dist_vpar_lant if dic['dist'] == min_dist]

            dist_parc_ant_2.append(vert_min_dist[0]) #distancias minimas de los vertices con problemas en el poligono de parcela a las lineas del antecedente

        max_dist = max(dic['dist'] for dic in dist_parc_ant_2)
        vert_max_dist = [dic for dic in dist_parc_ant_2 if dic['dist'] == max_dist]
        max_dist_2 = vert_max_dist["dist"]
    else:
        pass
    
    max_dist_2 = 0
    max_dist_3 = 0
    
    if len(vert_ant_chequeo)>0:
        dist_ant_parc_2 = list()
        
        for vert in vert_ant_chequeo:
            print("vert")
            print(vert)
            vert_ant =  Vec2(vert)
            print(vert_ant)
            dist_vant_lpar = list()
            for i in range(len(pol_medido)):
                dist = ezdxf.math.distance_point_line_2d(vert_ant,pol_medido[i-1], pol_medido[i])
                
                dist_vant_lpar.append({"dist":dist,"vant":[vert_ant[0],vert_ant[1]],"vp_1":[pol_medido[i-1]],"vp_2":pol_medido[i]})
            # Encontrar el valor mínimo de 'dist' en la lista de diccionarios
            min_dist = min(dic['dist'] for dic in dist_vant_lpar)

            # Filtrar la lista de diccionarios basándote en el valor mínimo de 'dist'
            vert_min_dist = [dic for dic in dist_vant_lpar if dic['dist'] == min_dist]

            dist_ant_parc_2.append(vert_min_dist[0]) #distancias minimas de los vertices con problemas en el poligono antecedente a las lineas de parcela
        print("dist_ant_parc_2")
        print(dist_ant_parc_2)

        print("dic['dist'] for dic in dist_ant_parc_2")
        print(dic['dist'] for dic in dist_ant_parc_2)
        max_dist = max([dic['dist'] for dic in dist_ant_parc_2])
        vert_max_dist = [dic for dic in dist_ant_parc_2 if dic['dist'] == max_dist]
        print("vert_max_dist")
        print(vert_max_dist)
        max_dist_3 = (vert_max_dist[0])["dist"]

    else:
        pass
    
    if len(vert_parc_chequeo)>0 or len(vert_ant_chequeo)>0:
        if float(max_dist_2 < tol) and float(max_dist_3) < tol:
            band = "georref_ok"
        else:
            band = "georref_error"
    else:
        band = "georref_ok"
    
    return band
