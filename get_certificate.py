import logging
import datetime
import certstream
import csv
import os

# Tableau pour stocker les certificats
certificates = []
max_certificates = 1000000  # Limiter à 1 million de certificats
save_interval = 1000  # Sauvegarder toutes les 1000 itérations

# Fonction pour sauvegarder les certificats dans un fichier CSV
def save_certificates_to_csv(certificates, filename='certificates.csv'):
    # Si le fichier existe déjà, on l'ouvre en mode ajout, sinon en mode écriture
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Écrire l'en-tête si c'est un nouveau fichier
        if not file_exists:
            writer.writerow(['Domain', 'As DER'])
        # Écrire les certificats dans le CSV
        for cert in certificates:
            writer.writerow([cert['domain'], cert['as_der']])

    print(f"Certificats sauvegardés dans '{filename}'.")

def print_callback(message, context):
    global certificates

    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        # Si nous avons atteint le nombre limite de certificats à stocker
        if len(certificates) >= max_certificates:
            return

        # Extraire les données du certificat
        cert_data = message['data']['leaf_cert']

        # Extraire les domaines associés au certificat
        all_domains = cert_data['all_domains']

        # Si aucun domaine n'est trouvé, définir à "NULL"
        if len(all_domains) == 0:
            domain = "NULL"
        else:
            domain = all_domains[0]

        # Créer un dictionnaire avec les informations essentielles du certificat
        cert_info = {
            "domain": domain,
            "as_der": cert_data['as_der']
        }
        print(len(certificates))
        # Ajouter le certificat au tableau
        certificates.append(cert_info)

        # Sauvegarder toutes les 1000 itérations
        if len(certificates) % save_interval == 0:
            save_certificates_to_csv(certificates)
            certificates.clear()  # Réinitialiser la liste des certificats

        # Optionnel : Afficher un message toutes les 1000 itérations pour vérifier
        if len(certificates) % 1000 == 0:
            print(f"{len(certificates)} certificats sauvegardés jusqu'à présent.")

# Configurer le logging
logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

# Connexion au flux CertStream
certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/full-stream')
