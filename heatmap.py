import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RangeSlider
from matplotlib.widgets import Button
from scipy.interpolate import griddata
import pandas as pd
from submodules.ldparser.ldparser import ldData
import threading
import tkinter as tk
from tkinter import filedialog

def save_csv_in_background(data, filename):
    """Sauvegarde le DataFrame en CSV dans un thread séparé."""
    def save_csv():
        data.to_csv(filename, index=False)
        print(f"Fichier CSV sauvegardé : {filename}")
    
    thread = threading.Thread(target=save_csv)
    thread.start()  # Démarre la sauvegarde en arrière-plan

def process_ld_file(l,name):
    target_freq = 500 # fréquence des données cibles temp ect

    #trouver l'index correspondant à la fréquence cible
    target_channel = next(chan for chan in l.channs if chan.freq == target_freq)
    target_channel_index = target_channel.data_len
    print(f"Le Csv comportera {target_channel_index} valeurs par channel")

    # Créer un index pour le DataFrame final
    new_index = range(0, target_channel_index)

    dataframes = []

    for i in l.channs :
        df = pd.DataFrame({i.name: i.data})
        if i.name == "TEMPS MODULE" or i.name == "TEMPS GROUP" or i.name == "TEMPS VALUE1" or i.name == "TEMPS VALUE2":
            dataframes.append(df)

    combined_df = pd.concat(dataframes, axis=1)
    combined_df.index = pd.Series([i / target_freq for i in new_index], name="Time")

    df = combined_df.reset_index()
    #keep  column temps_data = data[['TEMPS MODULE', 'TEMPS GROUP', 'TEMPS VALUE1', 'TEMPS VALUE2']].dropna()

    # Convert columns to numeric, ignoring non-numeric conversion errors
    temps_data = df[['TEMPS MODULE', 'TEMPS GROUP', 'TEMPS VALUE1', 'TEMPS VALUE2', 'Time']].dropna()
    temps_data['TEMPS MODULE'] = pd.to_numeric(temps_data['TEMPS MODULE'], errors='coerce')
    temps_data['TEMPS GROUP'] = pd.to_numeric(temps_data['TEMPS GROUP'], errors='coerce')
    temps_data['TEMPS VALUE1'] = pd.to_numeric(temps_data['TEMPS VALUE1'], errors='coerce')
    temps_data['TEMPS VALUE2'] = pd.to_numeric(temps_data['TEMPS VALUE2'], errors='coerce')

    #except for the column drop all the rows that are same as the previous row
    temps_data_unique = temps_data.loc[:, temps_data.columns != 'Time']
    temps_data_unique = temps_data_unique.drop_duplicates(keep='first')

    # Add the 'Time' column back to the DataFrame (aligning indexes)
    temps_data_unique['Time'] = temps_data.loc[temps_data_unique.index, 'Time']
    flattened_data = pd.DataFrame()

    for _, row in temps_data_unique.iterrows():
        module = int(row['TEMPS MODULE'])
        group = int(row['TEMPS GROUP'])
        col_name_value1 = f'Module_{module}_Group{group + 1}_Value1'
        col_name_value2 = f'Module_{module}_Group{group + 17}_Value2'
        flattened_data.at[row.name, col_name_value1] = row['TEMPS VALUE1']
        flattened_data.at[row.name, col_name_value2] = row['TEMPS VALUE2']

    flattened_data['Time'] = temps_data_unique['Time'].reset_index(drop=True)


    flattened_data['Time'] = pd.to_datetime(flattened_data['Time'], errors='coerce')
    flattened_data = flattened_data.sort_values(by='Time')
    flattened_data = flattened_data.ffill().bfill().drop_duplicates()

    # Sauvegarder les données dans un fichier CSV en arrière-plan
    save_csv_in_background(flattened_data, name)

    return flattened_data

def plot_heatmap(data):
    # 1 module de batterie fait 8 cellules par 16, donc 128 cellules par module
    # 1 batterie fait 6 modules, donc 768 cellules par batterie 
    # nous on a 32 sensors par modules donc 192 sensors par batterie
    # ils sont disposé 16 d'un coté d'une batterie et 16 de l'autre coté

    # en bref 12 slices de 16 sensors de maximum 12*16 par batterie
    # les coordonnées seront donc compris dans X[0,5](step 0,5), Y[0,19], Z[0,8] pour une batterie car c'est un parralèlogramme 

    # coordonnées Y,Z des sensors d'un module (16 sensors)
    map_module = [(18.5, 5), (16, 2), (17, 7), (13.5, 1), (15, 7), (12, 2), (10, 2), (13, 7), (11, 6), (9, 2), (13.5, 7), (11.5, 3), (12.5, 1), (15, 6), (15, 2), (17, 6), (2.5,5), (0.5,1), (5,6), (3,2), (7.5,7), (5.5,3), (6.5,1), (8.5,5), (10,6), (7.5,1), (9,7), (5.5,1), (3.5,1), (5.5,5), (1.5,1), (5,7)]

    num_sensors = len(data.columns) - 1  # - 1 pour exclure la colonne "Time"
    num_timestamps = data.shape[0]

    # Initialiser un tableau NumPy pour stocker les températures
    temperatures = np.zeros((num_timestamps, num_sensors))

    time = pd.to_datetime(data["Time"])

    # On instancie un tableau de 3 listes vides pour les coordonnées X, Y, Z et la temperature de chaque sensor d'en lordre des colones du csv 
    x = []
    y = []
    z = []
    module_numbers = []
    x_convert = [1,3,5,4,2,0]

    for idx, col_name in enumerate(data.columns):
        if col_name != "Time":
            # Nom de la colonne est genre "Module_4_Group6_Value1" donc on peut extraire "Module", "Group" et "Value" ne sert pas
            i_split = col_name.split("_")
            module = int(i_split[1])  # Extrait le numéro de module
            sensor = int(i_split[2][5:])  # Extrait le numéro de sensor

            # Déterminer la coordonnée X pour chaque module
            x_coord = x_convert[module]
            if module == 0 or module == 1 or module == 2:
                if 8 >= sensor or sensor >= 25 :
                    x_coord = x_coord + 0.5
                y_coord, z_coord = map_module[33-sensor-1]
            else :
                if 8 < sensor and sensor < 25 :
                    x_coord = x_coord + 0.5
                y_coord, z_coord = map_module[sensor-1]
            x.append(x_coord)
            
            # Déterminer les coordonnées Y et Z pour chaque sensor en utilisant map_module
            
            y.append(y_coord)
            z.append(z_coord)

            module_numbers.append(module)
            # Remplir le tableau de températures pour chaque point de temps
            temperatures[:, idx] = data[col_name].values  # Insérer les valeurs de température

    # Création de la grille d'interpolation
    def create_interpolation_grid(x_val, points_y, points_z, temp_values):
        y_min, y_max = min(points_y), max(points_y)
        z_min, z_max = min(points_z), max(points_z)
        
        grid_y, grid_z = np.mgrid[y_min:y_max:25j, z_min:z_max:25j]
        
        # Créer les points pour l'interpolation
        points = np.column_stack((points_y, points_z))
        grid_temp = griddata(points, temp_values, (grid_y, grid_z), method='cubic')
        
        return grid_y, grid_z, grid_temp


    # Configuration de la figure avec un espace réservé pour la colorbar
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(1, 2, width_ratios=[20, 1])  # Ratio pour le graphique principal et la colorbar
    ax = fig.add_subplot(gs[0], projection='3d')
    cax = fig.add_subplot(gs[1])  # Axe dédié pour la colorbar

    # Sliders
    ax_time = plt.axes([0.2, 0.02, 0.65, 0.03], facecolor="lightgoldenrodyellow")
    time_slider = Slider(ax_time, 'Temps', 0, num_timestamps - 1, valinit=0, valstep=1)
    for text_item in time_slider.ax.texts:
            text_item.remove()
    time_slider.valtext = time_slider.ax.text(0.5, 1.5, time[0], transform=time_slider.ax.transAxes,
                                              fontsize=10, verticalalignment='top', horizontalalignment='center')

    ax_z_cut = plt.axes([0.05, 0.25, 0.02, 0.63], facecolor="lightgoldenrodyellow")
    z_slider = Slider(ax_z_cut, 'Z Max', min(z), max(z), valinit=max(z), orientation='vertical')

    max_module = max(module_numbers)
    ax_module = plt.axes([0.2, 0.95, 0.65, 0.03], facecolor="lightgoldenrodyellow")
    module_slider = RangeSlider(ax_module, 'Plage de Modules', 0, max_module+0.5, 
                            valinit=(0, max_module+0.5), valstep=0.5)

    ax_opacity = plt.axes([0.95, 0.25, 0.02, 0.63], facecolor="lightgoldenrodyellow")
    opacity_slider = Slider(ax_opacity, 'Opacité', 0, 1, valinit=0.3, orientation='vertical')

    ax_button = plt.axes([0.935, 0.125, 0.05, 0.075])  # Positionnement du bouton (gauche, bas, largeur, hauteur)
    button = Button(ax_button, "Changer\nNorme")
    bouton = False

    def update(val):
        t = int(time_slider.val)
        seconds_since_epoch = (time[t] - pd.Timestamp("1970-01-01")) / pd.Timedelta(seconds=1)
        minutes = int(seconds_since_epoch // 60)
        seconds = int(seconds_since_epoch % 60)
        milliseconds = int((seconds_since_epoch % 1) * 1000)
        time_slider.valtext.set_text(time[t])
        time_str = f"{minutes} min {seconds} sec {milliseconds} ms"
        time_slider.valtext.set_text(str(seconds_since_epoch)+" s")
        z_max = z_slider.val
        x_min, x_max = module_slider.val  # Maintenant ces valeurs représentent directement les coordonnées X
        opacity = opacity_slider.val
        
        ax.cla()
        ax.grid(False)
        
        # Créer une normalisation commune
        filtered_temps = temperatures[t][temperatures[t] > 0]
        if len(filtered_temps) > 0:
            temp_min = np.min(filtered_temps)
            temp_max = np.max(filtered_temps)
        else:
            temp_min, temp_max = 0, 1

        if bouton : 
            norm = plt.Normalize(temp_min, temp_max)
        else :
            norm = plt.Normalize(min(temp_min, 20), max(temp_max, 50))
        
        # Filtrer tous les points qui sont dans la plage X
        mask_x = (np.array(x) >= x_min) & (np.array(x) <= x_max)
        
        # Obtenir les coordonnées X uniques dans la plage
        unique_x = np.unique(np.array(x)[mask_x])
        
        # Pour chaque coordonnée X unique
        for x_pos in unique_x:
            # Créer le masque pour cette position X
            mask = mask_x & (np.array(x) == x_pos) & \
                (np.array(z) <= z_max) & (temperatures[t] > 0)
            
            if np.any(mask):
                grid_y, grid_z, grid_temp = create_interpolation_grid(
                    x_pos,
                    np.array(y)[mask],
                    np.array(z)[mask],
                    temperatures[t][mask]
                )
                
                # Appliquer un masque pour les NaN dans la grille d'interpolation de température
                grid_temp = np.ma.masked_invalid(grid_temp)
                grid_y = np.ma.masked_where(grid_temp.mask, grid_y)
                grid_z = np.ma.masked_where(grid_temp.mask, grid_z)
                
                surf = ax.plot_surface(
                    np.full_like(grid_y, x_pos), grid_y, grid_z,
                    facecolors=plt.cm.jet(norm(grid_temp)),
                    alpha=opacity,
                    edgecolor='none',
                    rstride=1, cstride=1
                )
                
                ax.scatter(np.array(x)[mask], np.array(y)[mask], np.array(z)[mask],
                        c=temperatures[t][mask], cmap='jet', norm=norm, marker='o', s=100)

        # Configuration des axes
        ax.set_title("3D Heatmap de la Batterie avec Interpolation")
        ax.set_xlabel("X-axis (Modules)")
        ax.set_ylabel("Y-axis")
        ax.set_zlabel("Z-axis")
        
        cax.cla()
        plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='jet'), 
                    cax=cax, label='Température (°C)')
        
        fig.canvas.draw_idle()

    def toggle_norm(event):
        nonlocal bouton
        bouton = not bouton  # Alterne entre True et False
        update(0)  # Met à jour le graphique avec le nouvel état

    button.on_clicked(toggle_norm)
    # Lier les sliders
    time_slider.on_changed(update)
    z_slider.on_changed(update)
    module_slider.on_changed(update)
    opacity_slider.on_changed(update)

    # Afficher le plot initial
    update(0)
    plt.show()

def select_file_via_dialog():
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale Tkinter
    file_path = filedialog.askopenfilename(
        title="Choisissez un fichier .ld",
        filetypes=[("Fichiers LD", "*.ld"), ("Tous les fichiers", "*.*")]
    )
    return file_path


if len(sys.argv) != 2:
    print("Aucun fichier fourni en argument. Veuillez en sélectionner un via la boîte de dialogue.")
    file_path = select_file_via_dialog()
    if not file_path:  # Si aucun fichier n'a été sélectionné
        print("Erreur : Aucun fichier sélectionné. Fermeture du programme.")
        sys.exit(1)
else:
    # Récupérer le nom du fichier depuis les arguments
    file_path = sys.argv[1]

# Vérifier si le fichier a une extension .ld
if not file_path.lower().endswith('.ld'):
    print("Erreur: Le fichier fourni n'est pas un fichier ld.")
    sys.exit(1)

try:
    l = ldData.fromfile(file_path)
except Exception as e:
    print(f"Erreur lors du chargement du fichier : {e}")
    sys.exit(1)

print(l.head)
#print(list(map(str, l))) # list of channels
print()

if hasattr(sys, '_MEIPASS'):
    temp_dir = os.path.join(sys._MEIPASS, "data_temp")
else:
    temp_dir = "data_temp"

name = l.head.datetime.strftime(f"{temp_dir}/TEMP_%Y-%m-%d_%H-%M-%S.csv")

if os.path.exists(name):
    flattened_data = pd.read_csv(name)
else:
    flattened_data = process_ld_file(l,name)

# loader les données du csv
plot_heatmap(flattened_data)
