import re
import pandas as pd
from pathlib import Path

# Dossier où se trouvent les .txt générés par l'IA
base_dir = Path(__file__).resolve().parent
dossier_txt = base_dir / "resultats_2"
dossier_sortie = base_dir / "resultats_csv_par_groupe"
dossier_sortie.mkdir(exist_ok=True)

# Identifier tous les fichiers texte .txt par groupe
groupes = {}
for file in dossier_txt.glob("*.txt"):
    prefix = file.stem.split("_part")[0]  # ex: groupe_1
    groupes.setdefault(prefix, []).append(file)

def parse_file(filepath):
    records = []
    current_theme = None
    current_code = None
    fichier_nom = filepath.name

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Thème
            if line.startswith("### Thème") or line.startswith("- Thème") or line.startswith("**Thème"):
                m = re.match(r"[-#*]*\s*Thème\s*(\d+)?\s*[:\-]?\s*(.*)", line)
                if m:
                    current_theme = f"{m.group(1)}: {m.group(2)}" if m.group(1) else m.group(2)
                else:
                    current_theme = line.strip("#-* ").strip()
                continue

            # Code
            if line.startswith("* Code") or line.startswith("- Code") or line.startswith("1."):
                m = re.match(r"[-*0-9.]*\s*Code\s*(\d+)?\s*[:\-]?\s*(.*)", line)
                if m:
                    current_code = f"{m.group(1)}: {m.group(2)}" if m.group(1) else m.group(2)
                continue

            # Verbatim
            if "Verbatim" in line:
                m = re.match(r'.*Verbatim\s*[:\-]?\s*["“]?(.+?)["”]?\s*$', line)
                if m and current_theme and current_code:
                    records.append({
                        "Thème": current_theme,
                        "Code": current_code,
                        "Verbatim": m.group(1).strip(),
                        "Fichier": fichier_nom
                    })
    return records

# Traiter chaque groupe
for prefix, fichiers in groupes.items():
    all_data = []
    for fichier in fichiers:
        all_data.extend(parse_file(fichier))

    if not all_data:
        continue

    df = pd.DataFrame(all_data)
    df_clean = df.drop_duplicates(subset=["Verbatim"], keep="first")

    output_csv = dossier_sortie / f"{prefix}_grille_thematique.csv"
    df_clean.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"✅ Exporté : {output_csv.name}")
