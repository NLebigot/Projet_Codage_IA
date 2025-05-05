import os
import re
from dotenv import load_dotenv
from groq import Groq
import PyPDF2

# Charger la clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Clé API GROQ non trouvée dans .env")

client = Groq(api_key=api_key)

# 1. Fonction pour lire un PDF
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

# 2. Fonction de segmentation douce (par phrases, limite max)
def segmenter_par_phrase(texte, taille_max=10000):
    phrases = re.split(r'(?<=[.!?])\s+', texte)
    segments = []
    segment = ""

    for phrase in phrases:
        if len(segment) + len(phrase) + 1 <= taille_max:
            segment += phrase + " "
        else:
            segments.append(segment.strip())
            segment = phrase + " "
    if segment:
        segments.append(segment.strip())
    return segments

# 3. Dossiers
dossier_pdf = "entretiens"
dossier_sortie = "syntheses"
os.makedirs(dossier_sortie, exist_ok=True)

# 4. Traitement d’un seul fichier à la fois
nom_pdf = input("Nom du fichier PDF (dans 'entretiens/') à traiter : ").strip()
chemin_pdf = os.path.join(dossier_pdf, nom_pdf)
nom_base = os.path.splitext(nom_pdf)[0]

texte = lire_pdf(chemin_pdf)
segments = segmenter_par_phrase(texte, taille_max=10000)

synthese_entretien = ""

for idx, segment in enumerate(segments):
    prompt = f"""Tu es un sociologue. Ta mission est de produire une synthèse rédigée à partir du segment d’entretien ci-dessous.

Ta synthèse doit être :
- rédigée sous forme de texte fluide (pas de puces, pas de titres)
- fidèle au point de vue de l’enquêté : fais ressortir ses opinions, ressentis, formulations
- concise mais sociologiquement pertinente
- sans répéter la consigne ni réécrire ce prompt
- sans reformuler les idées anecdotiques ou trop répétées

Voici le segment à analyser :

{segment}
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        reponse = chat_completion.choices[0].message.content
        synthese_entretien += f"[Segment {idx + 1}]\n{reponse.strip()}\n\n"
        print(f"✅ Segment {idx + 1} traité")
    except Exception as e:
        print(f"⚠️ Erreur segment {idx + 1} :", str(e))

# 5. Sauvegarde de la synthèse complète
chemin_sortie = os.path.join(dossier_sortie, f"{nom_base}_synthese.txt")
with open(chemin_sortie, "w", encoding="utf-8") as f:
    f.write(synthese_entretien)

print(f"\n📄 Synthèse enregistrée dans : {chemin_sortie}")
