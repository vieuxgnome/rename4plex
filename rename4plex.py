import os
import re
import shutil
import requests
from urllib.parse import quote

# === CONFIGURATION ===
TMDB_API_KEY = 'TA_CLE_API_TMDB_ICI'
DOSSIER_SOURCE = r'M:\Films'
DOSSIER_DESTINATION = r'M:\Films\A copier'
DRY_RUN = True  # True = simulation, False = exécution réelle

# === FONCTIONS ===

def nettoyer_nom_fichier(nom_fichier):
    nom_sans_extension = os.path.splitext(nom_fichier)[0]
    nom_sans_extension = re.sub(r'[._]', ' ', nom_sans_extension)
    match = re.search(r'(19|20)\d{2}', nom_sans_extension)
    if match:
        annee = match.group()
        titre = nom_sans_extension[:match.start()].strip()
        return titre, annee
    return None, None

def chercher_tmdb(titre, annee):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={quote(titre)}&year={annee}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results']
    return []

def choisir_resultat(resultats):
    print("\nPlusieurs films trouvés :")
    for idx, film in enumerate(resultats):
        titre = film.get('title', 'Inconnu')
        date_sortie = film.get('release_date', 'N/A')
        print(f"{idx + 1}. {titre} ({date_sortie}) [id={film.get('id')}]")

    choix = input(f"Choisir un film (1-{len(resultats)}) ou 's' pour sauter : ")
    if choix.lower() == 's':
        return None
    try:
        idx = int(choix) - 1
        if 0 <= idx < len(resultats):
            return resultats[idx]
    except ValueError:
        pass
    return None

def generer_nom_fichier(titre, annee, tmdb_id, extension):
    titre_formate = titre.replace(':', ' -').replace('/', '-')  # Sécurité
    return f"{titre_formate} ({annee}) {{tmdb-{tmdb_id}}}{extension}"

def copier_fichier(ancien_chemin, nouveau_chemin):
    if DRY_RUN:
        print(f"[Dry-Run] Copier: {ancien_chemin} --> {nouveau_chemin}")
    else:
        shutil.copy2(ancien_chemin, nouveau_chemin)
        print(f"Copié: {ancien_chemin} --> {nouveau_chemin}")

# === SCRIPT PRINCIPAL ===

if not os.path.exists(DOSSIER_DESTINATION):
    os.makedirs(DOSSIER_DESTINATION)

for fichier in os.listdir(DOSSIER_SOURCE):
    if fichier.lower().endswith(('.mkv', '.mp4', '.avi')):
        chemin_fichier = os.path.join(DOSSIER_SOURCE, fichier)
        titre, annee = nettoyer_nom_fichier(fichier)

        if titre and annee:
            print(f"\nTraitement de: {fichier}")
            resultats = chercher_tmdb(titre, annee)

            film_choisi = None
            if len(resultats) == 1:
                film_choisi = resultats[0]
            elif len(resultats) > 1:
                film_choisi = choisir_resultat(resultats)

            if film_choisi:
                id_tmdb = film_choisi['id']
                titre_tmdb = film_choisi['title']
                extension = os.path.splitext(fichier)[1]
                nouveau_nom = generer_nom_fichier(titre_tmdb, annee, id_tmdb, extension)
                chemin_destination = os.path.join(DOSSIER_DESTINATION, nouveau_nom)

                copier_fichier(chemin_fichier, chemin_destination)
            else:
                print(f"Film ignoré: {titre} ({annee})")
        else:
            print(f"Impossible d'analyser: {fichier}")

print("\n--- Terminé ---")
if DRY_RUN:
    print("Dry-run seulement. Aucun fichier réellement copié.")
