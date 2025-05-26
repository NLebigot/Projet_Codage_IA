import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Clé API GROQ non trouvée")

client = Groq(api_key=api_key)

base_dir = os.path.dirname(__file__)
dossier_csv = os.path.join(base_dir, "resultats_csv_par_groupe")
limite_caracteres = 120000  # ≈ 30 000 tokens

# Charger les fichiers CSV
fichiers = sorted(f for f in os.listdir(dossier_csv) if f.endswith(".csv"))
groupes = {
    "synthese_A": fichiers[:3],  # groupe_1 à groupe_3
    "synthese_B": fichiers[3:]   # groupe_4 à groupe_6
}

syntheses = {}

# ÉTAPE 1 : Générer les synthèses A et B
for nom_synthese, fichiers_groupes in groupes.items():
    contenu = ""
    for f in fichiers_groupes:
        chemin = os.path.join(dossier_csv, f)
        df = pd.read_csv(chemin)
        for _, row in df.iterrows():
            contenu += f"\nThème : {row['Thème']}\n  Code : {row['Code']}\n    Verbatim : \"{row['Verbatim']}\"\n"

    if len(contenu) > limite_caracteres:
        print(f"⚠ {nom_synthese} dépasse {limite_caracteres} caractères. Tronquage automatique.")
        contenu = contenu[:limite_caracteres]

    prompt = (
        "Tu es un sociologue. Ton rôle est de comprendre et d'analyser de manière cohérente un ensemble de données issues d'entretiens sociologiques.\n\n"
        "Ces données prennent la forme de grilles thématiques construites à partir de propos d'étudiant·es interrogé·es sur leur usage de l’intelligence artificielle, notamment ChatGPT, dans un contexte académique.\n\n"
        "Ta tâche est double :\n\n"
        "1. Produis une synthèse sociologique exhaustive de ces grilles, sous forme de texte continu (pas de tableau). Elle doit mobiliser une lecture rigoureuse, nuancée et transversale. "
        "Dégage les grandes dynamiques sociales, tensions, représentations, pratiques et positionnements identifiés dans les propos. 👉 Cette synthèse doit faire au moins 1200 mots.\n\n"
        "2. Propose ensuite une analyse sociologique qualitative de ces thèmes : quelles interprétations sociologiques peut-on tirer de ces matériaux ? "
        "Quelles logiques sociales, rapports au savoir, figures d'autorité, inégalités ou postures étudiantes peut-on mettre en évidence ? 👉 Cette analyse doit faire au moins 800 mots.\n\n"
        "Ne résume pas mécaniquement. N’énumère pas. Ne présente pas de tableau. Utilise un ton interprétatif, analytique, et sociologiquement informé.\n\n"
        "Voici les grilles à analyser :\n"
        + contenu
    )

    print(f"🧠 Génération de la {nom_synthese}...")
    try:
        reponse = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        ).choices[0].message.content

        syntheses[nom_synthese] = reponse

        with open(os.path.join(base_dir, f"{nom_synthese}.txt"), "w", encoding="utf-8") as f_out:
            f_out.write(reponse)
        print(f"✅ {nom_synthese}.txt enregistré")

    except Exception as e:
        print(f"[Erreur] {nom_synthese} :", str(e))

# ÉTAPE 2 : Synthèse finale
if len(syntheses) == 2:
    contenu_final = syntheses["synthese_A"] + "\n\n" + syntheses["synthese_B"]
    if len(contenu_final) > limite_caracteres:
        print("⚠ Contenu combiné trop long, tronquage pour synthèse finale.")
        contenu_final = contenu_final[:limite_caracteres]

    prompt_final = (
        "Tu es un sociologue. Ton rôle est de comprendre et d'analyser de manière cohérente un ensemble de données issues d'entretiens sociologiques.\n\n"
        "Ces données prennent la forme de grilles thématiques construites à partir de propos d'étudiant·es interrogé·es sur leur usage de l’intelligence artificielle, notamment ChatGPT, dans un contexte académique.\n\n"
        "Ta tâche est double :\n\n"
        "1. Produis une synthèse sociologique exhaustive de ces grilles, sous forme de texte continu (pas de tableau). Elle doit mobiliser une lecture rigoureuse, nuancée et transversale. "
        "Dégage les grandes dynamiques sociales, tensions, représentations, pratiques et positionnements identifiés dans les propos. 👉 Cette synthèse doit faire au moins 1200 mots.\n\n"
        "2. Propose ensuite une analyse sociologique qualitative de ces thèmes : quelles interprétations sociologiques peut-on tirer de ces matériaux ? "
        "Quelles logiques sociales, rapports au savoir, figures d'autorité, inégalités ou postures étudiantes peut-on mettre en évidence ? 👉 Cette analyse doit faire au moins 800 mots.\n\n"
        "Ne résume pas mécaniquement. N’énumère pas. Ne présente pas de tableau. Utilise un ton interprétatif, analytique, et sociologiquement informé.\n\n"
        "Voici les grilles à analyser :\n"
        + contenu_final
    )

    print("🧠 Synthèse finale en cours...")
    try:
        reponse_finale = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_final}],
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        ).choices[0].message.content

        chemin_final = os.path.join(base_dir, "synthese_globale_finale.txt")
        with open(chemin_final, "w", encoding="utf-8") as f:
            f.write(reponse_finale)

        print("✅ Synthèse globale finale enregistrée :", chemin_final)

    except Exception as e:
        print("[Erreur] synthèse finale :", str(e))
