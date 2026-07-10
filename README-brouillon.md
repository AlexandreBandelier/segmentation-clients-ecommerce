📊 Analyse de Segmentation Client RFM & Pipeline de Données E-Commerce

📌 Présentation du Projet

Ce projet consiste en la mise en place d'un pipeline de données (ETL) automatisé pour analyser, segmenter et visualiser les performances de vente d'une boutique en ligne.

L'objectif business est d'identifier les différents profils de consommateurs au sein de la base client, et plus particulièrement de cibler précisément les clients à forte valeur historique devenus inactifs (les "Anciens VIP Dormants") afin de permettre à l'équipe marketing de lancer des campagnes de réactivation à fort retour sur investissement (ROI).

🛠️ Architecture du Projet & Flux de Données

Le flux de traitement des données est structuré de manière rigoureuse en 4 grandes étapes :

Extraction : Récupération des données brutes issues des ventes via un export WooCommerce (donnees_boutique_brutes.csv).

Transformation & Nettoyage (Python) :

Normalisation et typage des données financières (suppression des symboles monétaires, des espaces de milliers classiques et des espaces insécables \xa0 qui bloquent le traitement numérique).

Calcul des indicateurs comportementaux RFM (Récence, Fréquence, Montant) pour chaque client.

Algorithme de segmentation attribuant un profil marketing précis.

Anonymisation et conformité RGPD :

Création d'une copie de données dédiée à la publication publique (donnees_boutique_propres_portfolio.csv).

Remplacement des noms et identifiants par des clés uniques anonymisées (ex : Client_1, client_1).

Masquage automatique des données sensibles (Regex) : Déploiement d'un filtre automatique analysant l'ensemble des colonnes textuelles afin de détecter et de masquer à la source toute adresse e-mail saisie accidentellement dans un mauvais champ par l'utilisateur.

Visualisation (Power BI Web) : Connexion dynamique à la source de données hébergée sur GitHub pour générer un tableau de bord interactif d'aide à la décision.

💻 Détails techniques du pipeline (Python)

Le script de nettoyage pipeline.py automatise l'ensemble des règles de gestion complexes. Voici les deux briques technologiques majeures :

1. Normalisation et typage des données financières

Pour permettre à Power BI de réaliser des opérations mathématiques (comme la Somme du chiffre d'affaires), le script nettoie en profondeur les impuretés textuelles de WooCommerce :

```python
for col in ['Dépense totale', 'AOV']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace('€', '', regex=False)
        # Élimination des espaces classiques, tabulations et espaces insécables (\xa0)
        df[col] = df[col].str.replace(r'\s+', '', regex=True)
        df[col] = df[col].str.replace('\xa0', '', regex=False)
        df[col] = df[col].str.replace(',', '.', regex=False).str.strip()
        # Conversion finale en nombre décimal réel
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
```

2. Algorithme de détection et d'anonymisation des adresses e-mail

Afin de garantir le respect du RGPD sans altérer la structure du fichier, un scanner basé sur une expression régulière analyse dynamiquement toutes les cellules de texte de la table :

```python
def masquer_texte_email(texte):
    if pd.isna(texte):
        return texte
    texte_str = str(texte)
    # Expression régulière de détection de structure d'e-mail
    pattern_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    def remplacer(match):
        email_trouve = match.group(0)
        prefixe, domaine = email_trouve.split('@', 1)
        if len(prefixe) <= 2:
            return f"{prefixe}*****@{domaine}"
        return f"{prefixe[0]}*****{prefixe[-1]}@{domaine}"
    
    return re.sub(pattern_email, remplacer, text_str if 'text_str' in locals() else texte_str)
```

# Application dynamique sur l'ensemble des colonnes textuelles
```python
for col in df_portfolio.columns:
    if df_portfolio[col].dtype == 'object':
        df_portfolio[col] = df_portfolio[col].apply(masquer_texte_email)
```

📊 Tableau de Bord Power BI (Aide à la Décision)

Le rapport construit est entièrement interactif et s'articule autour de trois composants principaux :

Les KPIs Financiers & Volumétriques : Chiffre d'Affaires Global (Somme formatée en €), Nombre de Clients Uniques (Nombre distinct d'identifiants), et Panier Moyen historique (AOV).

La Structure de la Base Client (Graphique en Anneau) : Visualisation de la proportion de chaque segment (VIP, Nouveau, Client Régulier, À relancer, Ancien VIP Dormant).

Le Tableau Opérationnel (Table dynamique) : Liste filtrable des fiches clients anonymes contenant leur historique d'achat et leur récence d'inactivité.

💡 Scénario d'exploitation décisionnelle

En cliquant directement sur la tranche "Ancien VIP Dormant" du graphique en anneau, l'ensemble du tableau de bord se filtre instantanément. L'analyste ou le responsable marketing obtient immédiatement :

Le volume exact de clients concernés par cette cible.

Le manque à gagner financier précis représenté par ce segment dormant.

La liste des identifiants anonymes directement prête à être exportée pour lancer une campagne de réactivation ciblée.

🚀 Comment exécuter ce projet ?

Prérequis

Python 3.x installé sur votre machine.

La bibliothèque Pandas :

pip install pandas numpy


Exécution du pipeline

Placez votre fichier d'export WooCommerce dans le même dossier sous le nom donnees_boutique_brutes.csv.

Lancez le script de pipeline :

python pipeline.py


Deux fichiers nettoyés et segmentés sont générés automatiquement :

donnees_boutique_propres_interne.csv : Données d'entreprise non altérées.

donnees_boutique_propres_portfolio.csv : Version anonymisée et conforme RGPD pour la publication publique.
