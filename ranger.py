import os
import glob
import pandas as pd

def charger_et_parser_fichiers(entretien, dossier="resultats"):
    pattern = os.path.join(dossier, f"{entretien}_segment_*.txt")
    fichiers = sorted(glob.glob(pattern))
    data = []

    for fichier in fichiers:
        with open(fichier, "r", encoding="utf-8") as f:
            theme = None
            for ligne in f:
                ligne = ligne.strip()
                if ligne.startswith("**Thème"):
                    theme = ligne.strip("* ").strip(":")
                elif ligne.startswith("* Code"):
                    code = ligne.split(":", 1)[1].strip()
                elif ligne.startswith("+ Verbatim"):
                    verbatim = ligne.split(":", 1)[1].strip()
                    data.append((entretien, theme, code, verbatim, fichier))
    return pd.DataFrame(data, columns=["Entretien", "Thème", "Code", "Verbatim", "Fichier"])

def nettoyer_et_exporter(df, entretien):
    df_clean = df.drop_duplicates(subset=["Code", "Verbatim"]).sort_values(by=["Thème", "Fichier"])
    nom_csv = f"{entretien}_grille_thematique.csv"
    df_clean.to_csv(nom_csv, index=False, encoding="utf-8")
    print(f"✅ CSV généré : {nom_csv}")

if __name__ == "__main__":
    nom_entretien = input("Nom de l'entretien (ex: entretien_4) : ").strip()
    df = charger_et_parser_fichiers(nom_entretien, "resultats")
    nettoyer_et_exporter(df, nom_entretien)
