import ezdxf
from tkinter import messagebox, filedialog, ttk

def descargar_dxf(last_dir, parcelas_poly, manz_ant_posgba_2,parc_ant_posgba_2):          

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

