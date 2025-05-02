import os
from dotenv import load_dotenv
from groq import Groq
import PyPDF2

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Obtenir la clé API depuis le fichier .env
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Clé API non trouvée dans .env. Assurez-vous que GROQ_API_KEY est configurée.")

# Initialiser le client Groq
client = Groq(api_key=api_key)

# Fonction pour lire un fichier PDF et extraire son contenu
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
        print("Erreur lors de la lecture du PDF:", str(e))
    return contenu

# Fonction pour segmenter le texte en morceaux de taille spécifiée
def segmenter_texte(texte, taille_segment=10000):
    segments = []
    for i in range(0, len(texte), taille_segment):
        segments.append(texte[i:i + taille_segment])
    return segments

# Spécifiez le chemin vers votre fichier PDF ici
chemin_pdf = "1_loris.pdf"  # Nouveau nom de fichier PDF
texte_pdf = lire_pdf(chemin_pdf)

if not texte_pdf:
    raise ValueError("Le fichier PDF est vide ou n'a pas pu être lu.")

# Segmenter le texte en morceaux de 10 000 caractères
segments = segmenter_texte(texte_pdf, taille_segment=10000)

# Traiter chaque segment individuellement
for idx, segment in enumerate(segments):
    prompt = (
        "Ton but est de me créer un tableau thématique. En prenant un point de vue sociologique. "
        "Ce tableau sera celui d'un entretien sociologique, tu devras coder l'entretien avec les réponses. "
        "De l'enquêté uniquement. Tu devras après le code mettre le verbatim qui lui est associé. "
        "Une fois que tu as trouvé tous les codes associés aux réponses, tu devras ranger ces codes et verbatim dans un thème plus global si cela te semble cohérent et utile. "
        "Fais attention à ce que ce soit bien cohérent entre les codes que tu trouveras et de bien les ranger ensemble dans un thème qui leur va bien à tous. "
        "Nous allons dire qu'environ 10 codes pour un thème, mais ce n'est pas figé, si plus ou moins te semble essentiel vas-y. "
        "Attribue chaque code et verbatim à un seul thème. \n\n"
        f"Voici le texte :\n\n{segment}"
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        reponse = chat_completion.choices[0].message.content
        # Enregistrer la réponse dans un fichier texte
        nom_fichier = f"tableau_thematique_segment_{idx + 1}.txt"
        with open(nom_fichier, "w", encoding="utf-8") as f:
            f.write(reponse)
        print(f"Segment {idx + 1} traité et enregistré dans {nom_fichier}")
    except Exception as e:
        print(f"Une erreur s'est produite lors du traitement du segment {idx + 1} :", str(e))
