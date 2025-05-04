import os
from dotenv import load_dotenv
from groq import Groq
import PyPDF2

# Charger la clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Clé API GROQ non trouvée dans .env")

client = Groq(api_key=api_key)

# Fonctions
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

def segmenter_texte(texte, taille_segment=10000):
    return [texte[i:i + taille_segment] for i in range(0, len(texte), taille_segment)]

# Paramètres
dossier_pdf = "entretiens"
dossier_sortie = "resultats"
os.makedirs(dossier_sortie, exist_ok=True)

# --------- Traitement d’un seul fichier ---------
nom_fichier_pdf = input("Nom du fichier PDF à traiter (ex: entretien_4.pdf) : ").strip()
chemin_pdf = os.path.join(dossier_pdf, nom_fichier_pdf)
nom_entretien = os.path.splitext(nom_fichier_pdf)[0]

texte = lire_pdf(chemin_pdf)
if not texte:
    print("⚠ Fichier vide ou illisible.")
    exit()

segments = segmenter_texte(texte)

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
            model="llama-3.3-70b-versatile",
        )
        reponse = chat_completion.choices[0].message.content
        nom_fichier = f"{nom_entretien}_segment_{idx + 1}.txt"
        chemin_sortie = os.path.join(dossier_sortie, nom_fichier)
        with open(chemin_sortie, "w", encoding="utf-8") as f:
            f.write(reponse)
        print(f"✅ Segment {idx + 1} enregistré : {nom_fichier}")
    except Exception as e:
        print(f"[Erreur] Segment {idx + 1} :", str(e))
