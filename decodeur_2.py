import os
from dotenv import load_dotenv
from groq import Groq

# Initialisation
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Clé API GROQ non trouvée")

client = Groq(api_key=api_key)

# Config
racine_groupes = "."  # dossier racine où sont groupe_1, groupe_2, ...
dossier_sortie = "resultats_2"
limite_caracteres = 30000
os.makedirs(dossier_sortie, exist_ok=True)

# Traitement par groupe
for dossier in sorted(os.listdir(racine_groupes)):
    chemin_dossier = os.path.join(racine_groupes, dossier)
    if not (os.path.isdir(chemin_dossier) and dossier.startswith("groupe_")):
        continue

    fichiers_csv = sorted([
        f for f in os.listdir(chemin_dossier)
        if f.endswith(".csv") and "grille_thematique" in f
    ])

    if not fichiers_csv:
        continue

    print(f"🔍 Traitement de {dossier} avec {len(fichiers_csv)} fichiers")

    # Lire tous les contenus de fichiers du groupe
    fichiers_contenus = []
    for f in fichiers_csv:
        chemin = os.path.join(chemin_dossier, f)
        with open(chemin, "r", encoding="utf-8") as f_obj:
            contenu = f_obj.read()
            fichiers_contenus.append((f, contenu))

    # Segmenter en blocs de < 30 000 caractères
    segments = []
    segment = []
    longueur = 0

    for nom_fichier, contenu in fichiers_contenus:
        if longueur + len(contenu) > limite_caracteres:
            segments.append(segment)
            segment = [(nom_fichier, contenu)]
            longueur = len(contenu)
        else:
            segment.append((nom_fichier, contenu))
            longueur += len(contenu)

    if segment:
        segments.append(segment)

    # Génération de synthèse pour chaque segment du groupe
    for i, segment in enumerate(segments, start=1):
        prompt = (
            "Tu es un sociologue expert. Tu vas analyser un ensemble de grilles thématiques issues de plusieurs entretiens préalablement codés.\n"
            "Ton objectif est de produire une nouvelle grille de synthèse à partir de ces fichiers.\n\n"
            "Ta tâche :\n"
            "- Regrouper et reformuler les thèmes en 4 à 5 thèmes cohérents.\n"
            "- Sélectionner les codes les plus pertinents (10 par thème) même s'ils viennent de différents entretiens.\n"
            "- Pour chaque code, conserver un seul verbatim représentatif.\n"
            "- Respecter la structure suivante :\n"
            "  - Thème X : Titre\n"
            "    - Code X : Nom du code\n"
            "      - Verbatim : \"citation exacte\"\n\n"
            "Tu dois produire une grille finale unique, structurée et rigoureuse, sans mentionner les entretiens sources.\n\n"
            "Voici les grilles thématiques extraites :\n"
        )
        for nom_fichier, contenu in segment:
            prompt += f"\n\n--- Contenu du fichier {nom_fichier} ---\n{contenu}"

        try:
            reponse = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
            ).choices[0].message.content

            nom_fichier_sortie = f"{dossier}_part_{i}.txt"
            chemin_sortie = os.path.join(dossier_sortie, nom_fichier_sortie)

            with open(chemin_sortie, "w", encoding="utf-8") as f_out:
                f_out.write(reponse)

            print(f"✅ {nom_fichier_sortie} enregistré")

        except Exception as e:
            print(f"[Erreur] {dossier} part {i} :", str(e))
