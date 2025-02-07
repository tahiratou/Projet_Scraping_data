import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
import time
import csv
from selenium import webdriver # Importation du module Selenium
from selenium.webdriver.common.by import By # Importation du module By pour les éléments du navigateur
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import streamlit as st












#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Fonction pour scraper la page "Donnée du Réseau (mise à jour 5min)"

def scraper(engine, DonneeDuRéseau_5min):


    
    #Récuperation des données
    #----------------------------------------------------------------------------------------------------
    url = "https://tso.nbpower.com/Public/fr/SystemInformation_realtime.asp"
    r = requests.get(url)
    bs = BeautifulSoup(r.content, "html.parser")
    table = bs.find_all('table')
    font = bs.find_all('font')

    # Vérifier s'il y a au moins deux balises <table> et récupérer le contenu de la deuxième balise <table>
    if len(table) >= 2:
        deuxieme_table = table[1]
    # Vérifier s'il y a au moins 6 balises <font>
    if len(font) >= 6:
        font6 = font[4]
    # Vérifier s'il y a au moins trois balises <tr> et récupérer le contenu de la deuxième et troisième balises <tr>
    tr = deuxieme_table.find_all('tr')
    if len(tr) >= 3:
        tr2_data = [(td.text.strip()) for td in tr[1].find_all('td')]
        tr3_data = [(td.text.strip()) for td in tr[2].find_all('td')]
        font6_data = [(i.text.strip()) for i in font6.find_all('i')]



    # Traitement et transformation
    #----------------------------------------------------------------------------------------------------
    df = pd.DataFrame([tr2_data, tr3_data, font6_data])



    # Exportation des données
    #----------------------------------------------------------------------------------------------------
    # Vérifier si le fichier Excel existe
    if os.path.exists('donneesdureseau_5min.xlsx'):
        # Charger le DataFrame existant depuis le fichier Excel
        df_existing = pd.read_excel('donneesdureseau_5min.xlsx')

        # Concaténer le DataFrame existant avec le nouveau DataFrame
        df_combined = pd.concat([df_existing, df])
    else:
        # Si le fichier Excel n'existe pas, utiliser le nouveau DataFrame
        df_combined = df
    df_combined.to_excel('donneesdureseau_5min.xlsx', index=False)



    # Stockage dans la base de donnée
    #----------------------------------------------------------------------------------------------------
    # Créer une session SQLAlchemy pour interagir avec la base de donnée
    Session = sessionmaker(bind=engine)
    session = Session()

    # Créer un objet Donnee avec les données extraites
    Donnee_5min = DonneeDuRéseau_5min(
        charge_nb=tr3_data[0],
        demande_nb=tr3_data[1],
        iso_ne=tr3_data[2],
        emec=tr3_data[3],
        mps=tr3_data[4],
        quebec=tr3_data[5],
        nova_scotia=tr3_data[6],
        pei=tr3_data[7],
        marge_reserve_10min_non_synchrone=tr3_data[8],
        marge_reserve_10min_synchrone=tr3_data[9],
        marge_reserve_30min=tr3_data[10]
    )

    # Ajouter l'objet à la session et commit pour le stocker dans la base de données
    session.add(Donnee_5min)
    session.commit()



    # Visualisation 
    #----------------------------------------------------------------------------------------------------
    # Récupérer toutes les données de la table 'donnees'
    donnees = session.query(DonneeDuRéseau_5min).all()
    colonnes_a_extraire = ['date', 'charge_nb', 'demande_nb', 'iso_ne', 'emec', 'mps', 'quebec', 'nova_scotia', 'pei', 'marge_reserve_10min_non_synchrone', 'marge_reserve_10min_synchrone', 'marge_reserve_30min']

    # Initialiser un dictionnaire pour stocker les listes de données pour chaque colonne
    donnees_par_colonne = {colonne: [] for colonne in colonnes_a_extraire}
    # Extraire les données pour chaque colonne
    for donnee in donnees:
        for colonne in colonnes_a_extraire:
            donnees_par_colonne[colonne].append(getattr(donnee, colonne))

    # Tracer les données
    for colonne, valeurs in donnees_par_colonne.items():
        if colonne != 'date':  # Exclure la colonne 'date' du tracé
            plt.plot(donnees_par_colonne['date'], valeurs, marker='o', linestyle='-', label=colonne.capitalize())

    plt.xlabel('Timestamp')
    plt.ylabel('Valeur')
    plt.title('Évolution des valeurs au fil du temps')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show(block=False)
    plt.pause(10)
    plt.close()
    # Fermer la session
    session.close()









#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Fonction pour scraper la page "Données archivées"

def donnée_archivées(donnees_archivées, engine) : 
    # Créer une session pour interagir avec la base de données
    Session = sessionmaker(bind=engine)
    session = Session()
    all_data = []
    for annee in ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]:
        for mois in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            driver = webdriver.Chrome(executable_path = "C:/Users/AMADOU LOUM DIOP/Documents/chromedriver-win64/chromedriver.exe") # Création d'un objet driver pour le navigateur Chrome
            driver.get("https://tso.nbpower.com/Public/fr/system_information_archive.aspx") # Ouvre le navigateur et va sur le site


            # Attendre un court instant pour que la page se mette à jour
            time.sleep(1)
            

    
            #Récuperation des données
            #----------------------------------------------------------------------------------------------------
            # Sélectionner l'année dans la liste déroulante
            select_annee = driver.find_element(By.ID, "ctl00_cphMainContent_ddlYear")
            # Utiliser JavaScript pour définir la valeur de l'élément "select"
            driver.execute_script(f"arguments[0].value = '{annee}';", select_annee)

            # Attendre un court instant pour que la page se mette à jour
            time.sleep(1)

            # Sélectionner le mois dans la liste déroulante
            select_mois = driver.find_element(By.ID, "ctl00_cphMainContent_ddlMonth")
            # Utiliser JavaScript pour définir la valeur de l'élément "select"
            driver.execute_script(f"arguments[0].value = '{mois}';", select_mois)
            # Attendre un court instant pour que la page se mette à jour
            time.sleep(1)

            # Cliquez sur le lien "Obtenir les données"
            obtenir_donnees_link = driver.find_element(By.ID, "ctl00_cphMainContent_lbGetData")
            obtenir_donnees_link.click()

            # Attendre un court instant pour le chargement des données
            time.sleep(5)

            #Récupérer les données directement depuis le site avec BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pre_data = soup.find('pre')
                            


            # Traitement et transformation
            #----------------------------------------------------------------------------------------------------
            if pre_data:
                data_text = pre_data.get_text()
                # Traiter chaque ligne pour extraire les données
                lines = data_text.split('\n')
                header = lines[0].split(',')
                for line in lines[1:]:
                    data = line.split(',')
                    if len(data) == len(header):
                        data_dict = dict(zip(header, data))
                        all_data.append(data_dict)
                        


                        # Stockage dans la base de donnée
                        #----------------------------------------------------------------------------------------------------
                        # Ajouter les données à la base de données
                        donnee_obj = donnees_archivées(**data_dict)
                        session.add(donnee_obj)
                        session.commit()
            # Fermer le navigateur à la fin
            driver.quit()
        # Visualisation 
        #----------------------------------------------------------------------------------------------------
        #J'ai choisi de tracer les charges au NB de l'année 2017
        if annee == "2017" :
            donnees_2017 = [item["CHARGE_AU_NB"] for item in all_data]

            # Tracé
            plt.figure(figsize=(10, 6))

            plt.plot(donnees_2017, marker='o', linestyle='-', color='b', label=f"Évolution en {annee}")

            plt.xlabel("Données")
            plt.ylabel("CHARGE_AU_NB")
            plt.title(f"Évolution des données en {annee}")
            plt.legend()
            plt.grid(True)
            plt.show(block=False)
            plt.pause(10)
            plt.close()
    
    

    
    # Exportation des données
    #----------------------------------------------------------------------------------------------------

    # Enregistrer toutes les données dans un fichier CSV
    csv_file_path = "donnees_archivees.csv"
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=list(all_data[0].keys()))
        csv_writer.writeheader()
        csv_writer.writerows(all_data)












#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Fonction pour scraper la page "Interruption"

def interruption (engine, Interruption):
    #Configuration de Selenium
    driver = webdriver.Chrome(executable_path="C:/Users/AMADOU LOUM DIOP/Documents/chromedriver-win64/chromedriver.exe")  
    driver.get(url = 'https://tso.nbpower.com/Public/fr/outages.aspx')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Récupérer les éléments <a> avec la classe "popup"
    a_elements = driver.find_elements_by_css_selector('a.popup')

    # Récupérer le contenu de chaque balise <a> avec la classe "popup"
    interruption_numbers = [a.text.strip() for a in a_elements]

    #Récuperation des données
    #----------------------------------------------------------------------------------------------------
    for number in interruption_numbers:
    
        # Exécuter le script JavaScript pour ouvrir le dialogue et extraire les données
        script = """
            $('.popup').click();
            var data = {
                category: $('#mdlDetails .category').text(),
                forced_outage: $('#mdlDetails .forced-outage').text(),
                status: $('#mdlDetails .status').text(),
                planned_start: $('#mdlDetails .planned-start').text(),
                planned_stop: $('#mdlDetails .planned-stop').text(),
                queued_time: $('#mdlDetails .queued-time').text(),
                affected_interfaces: $('#mdlDetails .affected-interfaces').text(),
                purpose: $('#mdlDetails .purpose').text(),
                status_comments: $('#mdlDetails .status-comments').text(),
                interaction_impacts: $('#mdlDetails .interaction-impacts').text(),
                additional_information: $('#mdlDetails .additional-information').text(),
                mailto: $('#mdlDetails .mailto').attr('href')
            };
            return data;
        """
        data = driver.execute_script(script)
         


        # Stockage dans la base de donnée
        #----------------------------------------------------------------------------------------------------
        # Stocker les données dans une base de données
        interruption = Interruption(
            number=number,
            category=data['category'],
            forced_outage=data['forced_outage'],
            status=data['status'],
            planned_start=data['planned_start'],
            planned_stop=data['planned_stop'],
            queued_time=data['queued_time'],
            affected_interfaces=data['affected_interfaces'],
            purpose=data['purpose'],
            status_comments=data['status_comments'],
            interaction_impacts=data['interaction_impacts'],
            additional_information=data['additional_information'],
            mailto=data['mailto']
        )
        session.add(interruption)
        session.commit()

        time.sleep(3)
          


        # Exportation des données
        #----------------------------------------------------------------------------------------------------
        #Stocker les données dans un fichier texte
        with open(f'interruptions_transport.txt', 'a', encoding='utf-8') as txtfile:
            txtfile.write(f"\nInterruption De Transport #{number}\n") 
            for key, value in data.items():
                txtfile.write(f"{key}: {value}\n") 

        time.sleep(3)

        
        # Exécuter le script JavaScript pour cliquer sur le bouton Close
        script_close_dialogue = "$('#mdlDetails').dialog('close');"
        driver.execute_script(script_close_dialogue)
        time.sleep(3)
                  


    # Traitement et transformation
    #----------------------------------------------------------------------------------------------------
    # Charger les données depuis la base de données
    interruptions = session.query(Interruption).all()
    
    # Convertir les champs planned_start et planned_stop en objets datetime
    for interruption in interruptions:
        interruption.planned_start = datetime.strptime(interruption.planned_start, "%Y/%m/%d %H:%M")
        interruption.planned_stop = datetime.strptime(interruption.planned_stop, "%Y/%m/%d %H:%M")
 
    # Créer une liste de dates planifiées de début et de fin
    dates_start = [interruption.planned_start for interruption in interruptions]
    dates_stop = [interruption.planned_stop for interruption in interruptions]
     
   

    # Visualisation 
    #----------------------------------------------------------------------------------------------------
    # Tracé des dates planifiées de début
    plt.figure(figsize=(10, 6))
    plt.bar(interruption_numbers, dates_start, label='Planned Start', color='blue', alpha=0.7)

    # Tracé des dates planifiées de fin
    plt.bar(interruption_numbers, dates_stop, label='Planned Stop', color='red', alpha=0.7)

    plt.xlabel('Numéro d\'interruption')
    plt.ylabel('Date')
    plt.title('Planned Start and Planned Stop for Each Interruption')
    plt.xticks(interruption_numbers)
    plt.gca().xaxis.set_major_locator(MultipleLocator(1))  # Afficher uniquement des numéros entiers sur l'axe x
    plt.legend()
    plt.show(block=False)
    plt.pause(10)
    plt.close()
    # Fermer le navigateur après avoir terminé
    driver.quit()









#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Fonction pour scraper la page "Prévisions des charges"

def previsions_de_charges(prevision_charges, engine):
    
    # URL du répertoire principal contenant les dossiers
    url = 'https://tso.nbpower.com/Public/fr/op/market/report_list.aspx?path=/load%20forecast'
    driver = webdriver.Chrome(executable_path="C:/Users/AMADOU LOUM DIOP/Documents/chromedriver-win64/chromedriver.exe")
    driver.get(url)

    Session = sessionmaker(bind=engine)
    session = Session()
    ids = ["lv_1", "lv_2", "lv_3", "lv_4"]
    
    # Créer une liste pour stocker le contenu des fichiers CSV
    csv_content_list = []
        

    output_file='prevision_charges.csv' 
    with open(output_file, "w", encoding='utf-8') as f: 
        writer = csv.writer(f, delimiter = ' ', lineterminator='\n')
        #Récuperation des données
        #----------------------------------------------------------------------------------------------------
        # Cliquez sur les dossiers
        for id in ids:
            Dossier_link = driver.find_element(By.ID, id)
            Dossier_link.click()
            try:
                # Cliquez sur le dossier Archives
                driver.find_element(By.ID, "lv_1").click()
                time.sleep(5)
                
                # Cliquez sur les dossiers de 2004 à 2023
                for i in range(1, 21): 
                    année_id = "lv_" + str(i)
                    
                    try:
                        driver.find_element(By.ID, année_id).click()
                        # Cliquez sur les sous-dossiers
                        for j in range(1, 13): 
                            sous_dossier_id = "lv_" + str(j)
                            try:
                                driver.find_element(By.ID, sous_dossier_id).click()
                            
                                # Récupérer les liens des fichiers
                                links = driver.find_elements(By.CSS_SELECTOR, 'a[href$=".csv"]')
                                
                                # Récupérer le contenu de chaque fichier et l'ajouter à la liste
                                for link in links:
                                    file_url = link.get_attribute('href')
                                    response = requests.get(file_url)
                                    csv_content = response.text
                                    lines = csv_content.split('\n')
                                        
                                    for line in lines:
                                        if ',' in line:
                                            parts = line.split(',')
                                            number = parts[0]
                                            charge = int(parts[1])  # Convertir la partie après la virgule en entier
                                            csv_content_list.append({'number': number, 'charge': charge})
                                            # Exportation des données
                                            #----------------------------------------------------------------------------------------------------
    
                                            for db_data in csv_content_list:
                                                writer.writerow([db_data['number'], db_data['charge']])

                                    # Ajouter les données à la base de données
                                    for db_data in csv_content_list:
                                        prevision_charge = prevision_charges(number=db_data['number'], charge=db_data['charge'])
                                        session.add(prevision_charge)

                                    # Valider les changements dans la base de données
                                    session.commit()


                            except NoSuchElementException:
                                continue
                            # Revenir en arrière pour le prochain sous-dossier
                            driver.back()
                            time.sleep(2)
                    except NoSuchElementException:
                        continue         
                    # Revenir en arrière pour le prochain dossier
                    driver.back()
                    time.sleep(2)
                
            except NoSuchElementException:
                continue
            # Récupérer les liens des fichiers
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href$=".csv"]')
            # Récupérer le contenu de chaque fichier et l'ajouter à la liste
            for link in links:
                file_url = link.get_attribute('href')
                response = requests.get(file_url)
                csv_content = response.text
                lines = csv_content.split('\n')
                                        
                for line in lines:
                    if ',' in line:
                        parts = line.split(',')
                        number = parts[0]
                        charge = int(parts[1])  # Convertir la partie après la virgule en entier
                        csv_content_list.append({'number': number, 'charge': charge})

                        # Exportation des données
                        #----------------------------------------------------------------------------------------------------
                        for db_data in csv_content_list:
                            writer.writerow([db_data['number'], db_data['charge']])
                        # Ajouter les données à la base de données
                        for db_data in csv_content_list:
                            prevision_charge = prevision_charges(number=db_data['number'], charge=db_data['charge'])
                            session.add(prevision_charge)

                            # Valider les changements dans la base de données
                            session.commit()


                        # Revenir en arrière pour le prochain dossier
                        driver.back()
                        time.sleep(2) 



    # Visualition des données
    #----------------------------------------------------------------------------------------------------
    # Charger les données à partir du fichier CSV
    with open(output_file, "r", encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=' ', lineterminator='\n')
        data = list(csv_reader)

    target_number = "20041029000000AD"
    filtered_data = [line for line in data if line[0].startswith(target_number)]

    # Vérifier si des données sont disponibles pour le numéro spécifique
    if not filtered_data:
        st.warning(f"Aucune donnée disponible pour le numéro {target_number}")
    else:
        # Extraire les charges et créer un graphique
        charges = [int(line[1]) for line in filtered_data]

        # Générer la courbe
        plt.figure(figsize=(10, 6))
        plt.plot(charges, marker='o', linestyle='-', color='b', label=f"Évolution des charges pour le numéro {target_number}")

        plt.xlabel("Index")
        plt.ylabel("Charge")
        plt.title(f"Évolution des charges pour le numéro {target_number}")
        plt.legend()
        plt.show()
