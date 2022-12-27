from tkinter import *
import pandas as pd
from tkinter import filedialog
import customtkinter as ctk
import threading
from geopy import distance
import time
import math
# comment 
ctk.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

app = ctk.CTk()
app.geometry("420x390")
app.title("PCI Conflict Finder")

root = ctk.CTkFrame(master=app)
root.pack(pady=20, padx=20, fill="both", expand=True)
progressbar = ctk.CTkProgressBar(master=root,orientation=HORIZONTAL,  mode='determinate')
progressbar.set(0)

l=ctk.CTkLabel(root, text=" ")
ll=ctk.CTkLabel(root, text=" ")

stats=ctk.CTkLabel(root, text="-")
stats_cln=ctk.CTkLabel(root, text="-")

kml_title=ctk.CTkLabel(root, text="PCI Conflict Finder")
data_cln_title=ctk.CTkLabel(root, text="Conflict Distance (m):")
e=ctk.CTkEntry(root, width=120)

#status = Label(root, text = "Coded by: Ahmad Dawara", bd=2, relief=SUNKEN, anchor = E)
# -----------------------------------------------------
def opn():
    global fp
    fp=filedialog.askopenfilename()
# -----------------------------------------------------
def fun():
    thrd=threading.Thread(target=t_procs)
    thrd.start()
    return
# -----------------------------------------------------
def t_procs():
    strt=time.perf_counter()
    stats_cln.configure(text='Started')
    stats.configure(text='-')
  
    df = pd.read_csv(fp)

    df['SiteName'] = [x.split('_')[-0] for x in df['CellName']]
    df = df.drop_duplicates(subset='SiteName', keep="first")

    dfx=df[['SiteName','Longitude','Latitude']]
    dfx=dfx.reset_index()
    dfx=dfx.drop(['index'], axis=1)

    sites_lst=list(dfx['SiteName'])
    long_lst=list(dfx['Longitude'])
    lat_lst=list(dfx['Latitude'])

    i=0
    di={'Site_A': [],'Long_A':[],'Lat_A':[],
        'Site_B':[],'Long_B':[],'Lat_B':[]}

    shw=1
    l=len(sites_lst)
    dfs = pd.DataFrame(di)
    for c in sites_lst:
        per=i/l
        
        print(per)
        per=per*0.5
        progressbar.set(per)

        site_a_lst=[c for _ in range(l)]
        long_a_lst=[long_lst[i] for _ in range(l)]
        lat_a_lst=[lat_lst[i] for _ in range(l)]


        d={'Site_A': site_a_lst,'Long_A':long_a_lst,'Lat_A':lat_a_lst,
            'Site_B':sites_lst,'Long_B':long_lst,'Lat_B':lat_lst}

        dfxx = pd.DataFrame(d)
        dfs=pd.concat([dfs,dfxx],ignore_index=True,sort=False)

        i=i+1
    stats_cln.configure(text='Calculating Distance...')
    dd=e.get()
    dd=int(dd)
    dfs['dist(m)'] = dfs.apply(lambda r: distance.distance((r['Lat_A'],r['Long_A']),(r['Lat_B'],r['Long_B'])).km * 1000 , axis=1)
    dfs = dfs[dfs['dist(m)'] != 0]
    dfs['result'] = dfs.apply(lambda x:'1' if x['dist(m)'] < dd else "0", axis=1)
    dfz = dfs[dfs['result'] == '1']

    #dfz.to_csv('out_table_sites.csv',index=False)

    uniq_sites=dfz['Site_A'].unique()
    print(len(uniq_sites))
    dfp=df.loc[df['SiteName'].isin(uniq_sites)]
    dfp=dfp.reset_index()
    dfp=dfp.drop(['index'], axis=1)
    

    # ---------------------------------------------------------------------
    cells_lst=list(dfp['CellName'])
    long_lst=list(dfp['Longitude'])
    lat_lst=list(dfp['Latitude'])
    pci_lst=list(dfp['PhyCID'])
    
    
    ucells_list=dfp['CellName'].unique()
    i=0
    di={'Cell_A': [],'Long_A':[],'Lat_A':[],'PCI_A':[],
        'Cell_B':[],'Long_B':[],'Lat_B':[],'PCI_B':[]}

    shw=1
    l=len(ucells_list)
    dfc = pd.DataFrame(di)
    stats_cln.configure(text='Finding Conflicts...')
    for c in ucells_list:
        per=i/l
        per=per*0.5
        per=per+0.5
        progressbar.set(per)
        print(per)

        cell_a_lst=[c for _ in range(l)]
        long_a_lst=[long_lst[i] for _ in range(l)]
        lat_a_lst=[lat_lst[i] for _ in range(l)]
        pci_a_lst=[pci_lst[i] for _ in range(l)]

        d={'Cell_A': cell_a_lst,'Long_A':long_a_lst,'Lat_A':lat_a_lst,'PCI_A':pci_a_lst,
            'Cell_B':cells_lst,'Long_B':long_lst,'Lat_B':lat_lst,'PCI_B':pci_lst}

        dfx = pd.DataFrame(d)
        dfc=pd.concat([dfc,dfx],ignore_index=True,sort=False)

        i=i+1

    dfc['dist(m)'] = dfc.apply(lambda r: distance.distance((r['Lat_A'],r['Long_A']),(r['Lat_B'],r['Long_B'])).km * 1000 , axis=1)

    dfc['conflict_result'] = dfc.apply(lambda x : '1' if x['PCI_A'] == x['PCI_B'] and x['Cell_A'] != x['Cell_B'] and x['dist(m)'] < dd else "0", axis=1)

    stats_cln.configure(text='Saving The Result...')
    dfc = dfc[dfc['conflict_result'] == '1']
    dfc.to_csv('out_table_conf.csv',index=False)

    fnsh=time.perf_counter()
    if len(dfc)==0:
        stats_cln.configure(text='No PCI Conflict!')
    else:
        stats_cln.configure(text=f'Found {int(len(dfc))} Conflicts!')
    stats.configure(text=f'Done in {round((fnsh-strt)/60)} minute and {math.floor((fnsh-strt)%60)} seconds.')
    #print(f'Done in {round((fnsh-strt)/60)} minute and {math.floor((fnsh-strt)%60)} seconds.')

# -----------------------------------------------------
b_opn=ctk.CTkButton(root, text="Browse" ,command=opn)

b_browse_cln=ctk.CTkButton(root, text="Find Conflicts" ,command=fun)

# ----------------------------------------------------------
data_cln_title.grid(row = 3, column = 1,pady=10,padx=10)
e.grid(row = 3, column = 2, pady=10)


kml_title.grid(row = 1, column = 2,pady=10,padx=10)
b_opn.grid(row = 2, column = 2, pady=10)
progressbar.grid(row = 9, column = 2, pady=10)
b_browse_cln.grid(row = 15, column = 2, pady=10)
stats.grid(row = 10, column = 2, pady=10)
stats_cln.grid(row = 11, column = 2, pady=10)
# ---------------------------------------------------------

# ----------------------------------------------------------
app.mainloop()
