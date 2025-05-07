import os
import re
from dotenv import load_dotenv
from groq import Groq
import PyPDF2

# Charger la clé API depuis le .env
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Clé API GROQ non trouvée dans .env")

client = Groq(api_key=api_key)

# Lire un PDF et extraire le texte
def lire_pdf(chemin_pdf):
    contenu = ""
    try:
        with open(chemin_pdf, "rb") as fichier:
            lecteur = PyPDF2.PdfReader(fichier)
            for page in lecteur.pages:
                texte = page.extract_text()
                if texte:
                    contenu += texte
    except Exception as e:
        print(f"Erreur lecture PDF ({chemin_pdf}) :", str(e))
    return contenu

# Segmenter le texte à chaque prise de parole (après un ":")
def segmenter_par_parole(texte, taille_max=10000):
    blocs = re.split(r'(?<=:)', texte)  # garde le ":"
    segments = []
    segment = ""

    for bloc in blocs:
        if len(segment) + len(bloc) <= taille_max:
            segment += bloc
        else:
            segments.append(segment.strip())
            segment = bloc
    if segment:
        segments.append(segment.strip())

    return segments

# Dossiers
dossier_pdf = os.path.join("entretiens", "corpus entier")
dossier_sortie = "resultats"
os.makedirs(dossier_sortie, exist_ok=True)

# Parcourir tous les fichiers PDF
fichiers_pdf = [f for f in os.listdir(dossier_pdf) if f.endswith(".pdf")]

for fichier_pdf in fichiers_pdf:
    nom_entretien = os.path.splitext(fichier_pdf)[0]
    chemin_pdf = os.path.join(dossier_pdf, fichier_pdf)

    texte = lire_pdf(chemin_pdf)
    if not texte:
        print(f"⚠ Fichier vide ou illisible : {fichier_pdf}")
        continue

    segments = segmenter_par_parole(texte)

    for idx, segment in enumerate(segments):
        prompt = (
            "Tu es un sociologue. Ton objectif est d'analyser l'entretien suivant en respectant une méthode rigoureuse de codage qualitatif.\n\n"
            "1. Tu dois produire au moins 4 à 5 thèmes distincts par segment.\n"
            "2. Chaque thème doit contenir environ 10 codes avec leur verbatim associé.\n"
            "3. Chaque code doit être accompagné d’un verbatim clair et représentatif, issu uniquement des réponses de l’enquêté.\n"
            "4. Regroupe les codes dans un thème unique et cohérent. Ne crée pas de codes orphelins.\n"
            "5. Évite de reproduire les mêmes structures thématiques ou formulations que dans d'autres segments. Varie les angles d'analyse sociologique.\n"
            "6. N'écris pas un total de 10 codes à répartir sur plusieurs thèmes. Chaque thème doit être riche et structurant.\n\n"
            "Structure de sortie attendue :\n"
            "- Thème 1 : Titre du thème\n"
            "  - Code 1 : [intitulé du code]\n"
            "    - Verbatim : \"[citation textuelle de l'enquêté]\"\n"
            "  - ...\n"
            "  - Code 10 : ...\n"
            "- Thème 2 : ... (même format)\n\n"
            f"Voici le texte :\n\n{segment}"
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
            )
            reponse = chat_completion.choices[0].message.content
            nom_fichier = f"{nom_entretien}_segment_{idx + 1}.txt"
            chemin_sortie = os.path.join(dossier_sortie, nom_fichier)
            with open(chemin_sortie, "w", encoding="utf-8") as f:
                f.write(reponse)
            print(f"✅ {nom_fichier} enregistré")
        except Exception as e:
            print(f"[Erreur] {nom_entretien} segment {idx + 1} :", str(e))
