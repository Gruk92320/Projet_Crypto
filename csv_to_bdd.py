import pandas as pd
import mysql.connector

# Charger le fichier CSV
csv_file = "C:\\Users\\coren\\Downloads\\certificates.csv"
df = pd.read_csv(csv_file)

#################### fournit par chatgpt ###############################################

# Vérifier les colonnes du DataFrame
print("Colonnes disponibles :", df.columns)

# Vérifier que les colonnes attendues sont présentes
if 'name' not in df.columns or 'cle' not in df.columns:
    raise ValueError("Les colonnes 'name' ou 'cle' sont manquantes dans le fichier CSV.")

# Nettoyer les données : Supprimer les lignes avec des valeurs manquantes dans 'name' ou 'cle'
df = df.dropna(subset=['name', 'cle'])

# Ajouter les balises BEGIN CERTIFICATE et END CERTIFICATE autour des clés dans 'cle'
df['cle'] = df['cle'].apply(lambda x: f"-----BEGIN CERTIFICATE-----{x}-----END CERTIFICATE-----")

#############################################################################################


# Connexion à la base MySQL
conn = mysql.connector.connect(
    host="localhost",       
    user="root",            
    password="1234",        
    database="mydb"         
)

cursor = conn.cursor()
#compteur d'entrée remis à zéros toutes les 1000 entrées pour éviter de perdre les données
counter = 0    

for _, row in df.iterrows():

    cursor.execute("INSERT INTO crypto (name, cle) VALUES (%s, %s)", (row['name'], row['cle']))
    counter += 1

    # commit tout les 1000
    if counter == 1000:
        counter = 0
        conn.commit()
        print(f"{counter} entrees")

# commit avec les dernières entrées
conn.commit()
print(f"+ {counter} entrees")

# Fermer la connexion
cursor.close()
conn.close()
