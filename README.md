# Batterie 3D Heatmap - Visualisation des Températures

## Sommaire
- [Batterie 3D Heatmap - Visualisation des Températures](#batterie-3d-heatmap---visualisation-des-températures)
  - [Sommaire](#sommaire)
  - [Description du Programme](#description-du-programme)
    - [Fonctionnalités :](#fonctionnalités-)
  - [Description de la Batterie](#description-de-la-batterie)
    - [Structure :](#structure-)
    - [Coordonnées :](#coordonnées-)
  - [Instructions d'Installation et de Configuration](#instructions-dinstallation-et-de-configuration)
    - [Prérequis](#prérequis)
    - [Installation](#installation)
  - [Instructions d'Utilisation](#instructions-dutilisation)
  - [Les Sliders et leur Utilisation](#les-sliders-et-leur-utilisation)
  - [Photos et Justification du Mapping](#photos-et-justification-du-mapping)
    - [Mapping des thermistances](#mapping-des-thermistances)
      - [Face Gauche](#face-gauche)
      - [Face Droite](#face-droite)
    - [Mapping des modules](#mapping-des-modules)
      - [Vue du dessus](#vue-du-dessus)

---

## Description du Programme

Ce programme visualise une carte thermique (heatmap) 3D des températures dans une batterie composée de plusieurs modules. Les données sont extraites d'un fichier CSV contenant les relevés de température de différents capteurs disposés dans les modules de la batterie. Grâce à une interface interactive avec des sliders, l'utilisateur peut ajuster la plage temporelle, les niveaux Z, la plage des modules, ainsi que la transparence des surfaces affichées. 

### Fonctionnalités :
- Interpolation des données pour une visualisation fluide.
- Sélection interactive des plages de données.
- Génération dynamique de surfaces colorées basées sur les températures.

---

## Description de la Batterie

### Structure :
- **Modules et Cellules** : Une batterie est composée de **6 modules** contenant chacun **128 cellules** (16 x 8). Cela donne un total de **768 cellules** pour une batterie.
- **Capteurs** : Chaque module possède **32 capteurs**, soit un total de **192 capteurs** pour la batterie. Ces capteurs sont répartis de manière égale de chaque côté d’un module.

### Coordonnées :
- Les capteurs sont mappés sur un espace 3D défini par les axes **X**, **Y**, et **Z** :
  - **X** représente les modules (valeurs : 0 à 5.5), par exemple le premier module a gauche qui est le 6  aura sa face gauche à 0 et sa face droite à 0.5.
  - **Y** et **Z** correspondent aux positions des capteurs dépendamment de la face d'un module (voir photos pour plus de détails).
---

## Instructions d'Installation et de Configuration

### Prérequis
1. **Python** : Assurez-vous que Python 3.7 ou supérieur est installé. Vérifiez avec :
   ```bash
   python --version
   ```
2.	**Bibliothèques requises** : Le programme dépend de bibliothèques comme `numpy`, `matplotlib`, `pandas` et `scipy`. Ces bibliothèques sont listées dans requirements.txt.

### Installation
1.	**Cloner le dépôt** :
      ```bash
      git clone ssh://git@gitlab.fsae.polymtl.ca:9034/fsae/application/accumulator-heatmap.git
      cd accumulator-heatmap
      ```
2.	**Installer les dépendances** :
      ```bash
      pip install -r requirements.txt
      ```
---

## Instructions d'Utilisation

1. **Exécuter le script** : 
   ```bash
   python script.py fichier_donnees.csv
   ```
   Assurez-vous que le fichier CSV contient des colonnes correctement formatées avec les relevés de température.

2. **Interface Interactive** : Le programme affiche une fenêtre avec :
   - La visualisation 3D de la batterie.
   - Les sliders pour personnaliser l’affichage.

3. **Navigation** :
   - Déplacez-vous dans la visualisation à l'aide de la souris pour explorer les données sous différents angles.

---

## Les Sliders et leur Utilisation

1. **Temps** (Horizontal, bas) :
   - **Position** : En bas de la fenêtre.
   - **Fonction** : Permet de sélectionner un instant précis pour afficher les données de température correspondantes.

2. **Z Max** (Vertical, gauche) :
   - **Position** : À gauche.
   - **Fonction** : Ajuste la hauteur maximale (axe Z) des points et des surfaces affichées.

3. **Plage de Modules** (Horizontal, haut) :
   - **Position** : En haut.
   - **Fonction** : Limite l’affichage aux modules sélectionnés sur l’axe X.
> **🚨 WARNING 🚨**  
> La plage de modules retire les capteurs côté par côté et non par module entier.

1. **Opacité** (Vertical, droite) :
   - **Position** : À droite.
   - **Fonction** : Modifie la transparence des surfaces affichées pour améliorer la visibilité des points.

---

## Photos et Justification du Mapping

### Mapping des thermistances
Les photos ci-dessous montrent les faces gauche et droite d’un module, avec les coordonnées (Y, Z) des capteurs avec le numéro du capteur associé.

#### Face Gauche
![Face Gauche](images/left.png)

#### Face Droite
![Face Droite](images/right.png)

### Mapping des modules
La photo ci dessous décrit la position du module en fonction de son numéro.
> **Note 📒**  
> Le placement des thermistances est inversé un module sur deux, comme annoté sur la figure (seul le numéro des thermistances dans les coins supérieurs ont été notés).
#### Vue du dessus
![Vue du dessus](images/top.png)

---

Merci d'utiliser ce programme ! 😊