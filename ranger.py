import os
import glob
import pandas as pd

def charger_et_parser_fichiers(prefix="tableau_thematique_segment_", extension=".txt"):
    fichiers = sorted(glob.glob(f"{prefix}*{extension}"))
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
                    data.append((theme, code, verbatim, fichier))
    return pd.DataFrame(data, columns=["Thème", "Code", "Verbatim", "Fichier"])

def nettoyer_doublons(df):
    # Supprimer les doublons sur Code + Verbatim (on conserve le 1er thème rencontré)
    df_clean = df.drop_duplicates(subset=["Code", "Verbatim"])
    return df_clean.reset_index(drop=True)

def trier_par_theme_et_segment(df):
    return df.sort_values(by=["Thème", "Fichier"]).reset_index(drop=True)

def sauvegarder_csv(df, nom_fichier="grille_thematique_fusionnee.csv"):
    df.to_csv(nom_fichier, index=False, encoding="utf-8")
    print(f"✅ CSV sauvegardé : {nom_fichier}")

if __name__ == "__main__":
    df = charger_et_parser_fichiers()
    df_clean = nettoyer_doublons(df)
    df_trie = trier_par_theme_et_segment(df_clean)
    sauvegarder_csv(df_trie)
