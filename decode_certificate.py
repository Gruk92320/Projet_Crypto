import mysql.connector
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

# Connexion à la base de données
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="mydb"
)
cursor = db_connection.cursor()

def extract_rsa(cert_pem):
    cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
    public_key = cert.public_key()

    if isinstance(public_key, rsa.RSAPublicKey):
        public_numbers = public_key.public_numbers()
        modulus = public_numbers.n
        exponent = public_numbers.e
        key_size = public_key.key_size
        return modulus, key_size
    else:
        return None, None

# Récupérer les certificats de la table
cursor.execute("SELECT idcrypto, cle FROM crypto")
i=0

for row in cursor.fetchall():
    cert_id = row[0]
    cert_pem = row[1]

    # Extraire les informations de la clé publique
    modulus, key_size = extract_rsa_key_details(cert_pem.encode())

    if modulus and key_size:

        cursor.execute("""
            UPDATE crypto
            SET modulus = %s, key_size = %s
            WHERE idcrypto = %s
        """, (str(modulus), key_size, cert_id))
        i=i+1
    print(i)

db_connection.commit()
cursor.close()
db_connection.close()
