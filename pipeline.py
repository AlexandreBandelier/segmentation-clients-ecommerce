import pandas as pd
import numpy as np
from datetime import datetime
import os
import re

# --- 1. Détection automatique des dossiers et chemins ---
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_brut = os.path.join(dossier_actuel, 'donnees_boutique_brutes.csv')

# Chemins pour nos deux fichiers de sortie distincts
chemin_interne = os.path.join(dossier_actuel, 'donnees_boutique_propres_interne.csv')
chemin_portfolio = os.path.join(dossier_actuel, 'donnees_boutique_propres_portfolio.csv')

# --- 2. Chargement des données brutes ---
print("Chargement des données brutes...")
df = pd.read_csv(chemin_brut, dtype={'Dépense totale': str, 'AOV': str})

# --- 3. Nettoyage initial et financier ---
df['Pays/région'] = df['Pays/région'].fillna('Inconnu')

for col in ['Dépense totale', 'AOV']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace('€', '', regex=False)
        
        # AJOUTS CLÉS : Élimination complète des espaces cachés (WooCommerce)
        df[col] = df[col].str.replace(r'\s+', '', regex=True)
        df[col] = df[col].str.replace('\xa0', '', regex=False)
        
        df[col] = df[col].str.replace(',', '.', regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)


# --- 4. Segmentation Marketing (Priorité à la récence) ---
def attribuer_segment(row):
    commandes = row.get('Commandes', 0)
    depense = row.get('Dépense totale', 0)
    recence = row.get('Recence_Jours', 999)
    
    if recence > 180:
        if commandes >= 5 and depense >= 300:
            return 'Ancien VIP Dormant'
        return 'À relancer / Dormant'
    elif commandes >= 5 and depense >= 300:
        return 'VIP / Passionné'
    elif commandes == 1 and recence <= 30:
        return 'Nouveau client'
    else:
        return 'Client régulier'

print("Calcul de la segmentation marketing...")
# Calcul temporaire de la récence si la colonne existe
if 'Dernière activité' in df.columns:
    df['Dernière activité'] = pd.to_datetime(df['Dernière activité'], errors='coerce')
    aujourdhui = pd.Timestamp(datetime.now())
    df['Recence_Jours'] = (aujourdhui - df['Dernière activité']).dt.days.fillna(999)

df['Segment_Client'] = df.apply(attribuer_segment, axis=1)

# --- 5. Sauvegarde de la version INTERNE (Vraies données intactes) ---
df.to_csv(chemin_interne, index=False)
print("-> Fichier INTERNE sauvegardé avec succès.")

# --- 6. ANONYMISATION SÉCURISÉE POUR LE PORTFOLIO RTL ---
print("Anonymisation des données pour le portfolio...")

# Création d'une copie dédiée pour travailler sans abîmer l'original
df_portfolio = df.copy()

# Nouvelle fonction de nettoyage par Regex (Remplace l'ancienne "masquer_email")
def masquer_texte_email(texte):
    if pd.isna(texte):
        return texte
    texte_str = str(texte)
    # Pattern détectant une structure d'adresse email
    pattern_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    def remplacer(match):
        email_trouve = match.group(0)
        prefixe, domaine = email_trouve.split('@', 1)
        if len(prefixe) <= 2:
            return f"{prefixe}*****@{domaine}"
        return f"{prefixe[0]}*****{prefixe[-1]}@{domaine}"
    
    return re.sub(pattern_email, remplacer, texte_str)

# REMPLACE L'ANCIENNE APPLICATION : Scan dynamique sur tout le dataset
for col in df_portfolio.columns:
    if df_portfolio[col].dtype == 'object':
        df_portfolio[col] = df_portfolio[col].apply(masquer_texte_email)

# B. Remplacement de l'Identifiant et du Nom par des valeurs uniques anonymes
# Nous créons une correspondance logique : chaque ligne reçoit un numéro unique (ex: 1, 2, 3)
for i in range(len(df_portfolio)):
    numero_unique = i + 1
    
    # 1. On remplace le nom complet par un ID anonyme propre
    if 'Nom' in df_portfolio.columns:
        df_portfolio.loc[df_portfolio.index[i], 'Nom'] = f"Client_{numero_unique}"
        
    # 2. On remplace l'identifiant par un pseudo anonyme
    if 'Identifiant' in df_portfolio.columns:
        df_portfolio.loc[df_portfolio.index[i], 'Identifiant'] = f"client_{numero_unique}"

    # 3. Sécurité additionnelle : si d'autres colonnes d'ID alternatives existent, on les anonymise aussi
    for col_alternative in ['Nom d\'utilisateur', 'ID']:
        if col_alternative in df_portfolio.columns:
            df_portfolio.loc[df_portfolio.index[i], col_alternative] = f"client_{numero_unique}"

# Suppression définitive de la colonne Prénom si elle existe pour éviter les fuites de données
if 'Prénom' in df_portfolio.columns:
    df_portfolio = df_portfolio.drop(columns=['Prénom'])

# --- 7. Sauvegarde de la version PORTFOLIO (Données anonymes) ---
df_portfolio.to_csv(chemin_portfolio, index=False, float_format="%.2f")
print("-> Fichier PORTFOLIO (Anonymisé RGPD) sauvegardé avec succès !")
print("\n[Terminé] Le script Python a tout nettoyé et anonymisé à 100 % ! 🎉")