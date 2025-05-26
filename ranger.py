import re
import pandas as pd
from pathlib import Path

# Dossier du projet
base_dir = Path(__file__).resolve().parent
dossier_resultats = base_dir / "resultats"

# Identifier tous les fichiers texte .txt dans le dossier 'resultats'
interviews = {}
for file in dossier_resultats.glob("*.txt"):
    prefix = file.stem.split("_")[0]  # ex: D2SN5
    prefix = prefix.upper()  # normaliser LAU3, lau3 etc.
    interviews.setdefault(prefix, []).append(file)

def parse_file(filepath):
    records = []
    current_theme = None
    current_code = None
    entretien = filepath.stem.split("_")[0].upper()

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Thèmes
            if line.startswith("### Thème"):
                m = re.match(r"#{3}\s*Thème\s*(\d+)\s*[:\-]?\s*(.*)", line)
                if m:
                    current_theme = f"{m.group(1)}: {m.group(2)}"
                else:
                    current_theme = line.strip("# ").strip()
                continue
            elif line.startswith("- Thème"):
                m = re.match(r"-\s*Thème\s*[:\-]?\s*(.*)", line)
                if m:
                    current_theme = m.group(1)
                continue

            # Codes
            if line.startswith("- Code"):
                m = re.match(r"-\s*Code\s*(\d+)?\s*[:\-]?\s*(.*)", line)
                if m:
                    current_code = f"{m.group(1)}: {m.group(2)}" if m.group(1) else m.group(2)
                continue

            # Verbatims
            if line.startswith("- Verbatim"):
                m = re.match(r'-\s*Verbatim\s*[:\-]?\s*["“]?(.+?)["”]?\s*$', line)
                if m and current_theme and current_code:
                    records.append({
                        "Entretien": entretien,
                        "Thème": current_theme,
                        "Code": current_code,
                        "Verbatim": m.group(1).strip(),
                        "Fichier": filepath.name
                    })
    return records

# Traiter chaque entretien
for entretien, fichiers in interviews.items():
    all_data = []
    for fichier in fichiers:
        all_data.extend(parse_file(fichier))

    if not all_data:
        continue

    df = pd.DataFrame(all_data)

    # Supprimer les verbatim dupliqués (même si Code ou Thème changent)
    df_clean = df.drop_duplicates(subset=["Verbatim"], keep="first")

    # Exporter le CSV dans le même dossier "resultats"
    output_csv = dossier_resultats / f"{entretien}_grille_thematique.csv"
    df_clean.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"✅ Exporté : {output_csv.name}")
