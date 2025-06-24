from tkinter import messagebox, filedialog, ttk

def mostrar_resumen(smp, area_parc_dxf, area_excedente_dxf, plantas_dxf, sup_cub_dxf_f, sup_semicub_dxf_f, sup_descub_dxf_f, sup_emp_dxf, sup_nueva_dxf):
    if len(smp)==1:
        nom_parc=smp[0]
    else:
        nom_parc= "Error"
    
    cubierta_dxf = round(sum(sup_cub_dxf_f),2)
    semicubierta_dxf = round(sum(sup_semicub_dxf_f),2)
    descubierta_dxf = round(sum(sup_descub_dxf_f),2)

    return(print(messagebox.showinfo(title="Resumen Archivo DXF",message=f"SMP: {nom_parc}\nSup. Parc: {area_parc_dxf}\n\nSup. excedente: {area_excedente_dxf}\n\nN° de Plantas: {plantas_dxf}\n\nSup. Cubierta:{cubierta_dxf}\nSup semicub.: {semicubierta_dxf}\nSup. Descub: {descubierta_dxf}\n\nSup. Empadronada: {sup_emp_dxf}\nSup. A empadronar: {sup_nueva_dxf}")))

    