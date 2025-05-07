import os
import glob
import pandas as pd
import re

def charger_et_parser_fichiers(entretien, dossier="resultats"):
    pattern = os.path.join(dossier, f"{entretien}_segment*.txt")
    fichiers = sorted(glob.glob(pattern))
    data = []

    for fichier in fichiers:
        with open(fichier, "r", encoding="utf-8") as f:
            theme = None
            code = None
            for ligne in f:
                ligne = ligne.strip()
                # Détection souple du thème
                if re.match(r".*Thème\s*\d*\s*:", ligne, re.IGNORECASE):
                    theme = ligne.split(":", 1)[-1].strip()
                # Détection souple du code
                elif "Code" in ligne:
                    code = ligne.split(":", 1)[-1].strip()
                # Détection souple du verbatim
                elif "Verbatim" in ligne:
                    verbatim = ligne.split(":", 1)[-1].strip()
                    data.append((entretien, theme, code, verbatim, os.path.basename(fichier)))
    return pd.DataFrame(data, columns=["Entretien", "Thème", "Code", "Verbatim", "Fichier"])

def nettoyer_et_exporter(df, entretien):
    df_clean = df.drop_duplicates(subset=["Code", "Verbatim"]).sort_values(by=["Thème", "Fichier"])
    nom_csv = f"{entretien}_grille_thematique.csv"
    df_clean.to_csv(nom_csv, index=False, encoding="utf-8")
    print(f"✅ CSV généré : {nom_csv}")
    print(f"🔢 Codes uniques : {len(df_clean)} | 🧩 Thèmes détectés : {df_clean['Thème'].nunique()}")

if __name__ == "__main__":
    nom_entretien = input("Nom de l'entretien (ex: Lau1 ou D2SN11) : ").strip()
    df = charger_et_parser_fichiers(nom_entretien, "resultats")
    if df.empty:
        print("⚠ Aucun code/verbatim trouvé. Vérifie le format des fichiers ou augmente la tolérance du parsing.")
    else:
        nettoyer_et_exporter(df, nom_entretien)
