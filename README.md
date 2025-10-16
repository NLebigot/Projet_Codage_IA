Analyse qualitative de l’usage de ChatGPT en contexte universitaire
Objectif

Ce projet analyse qualitativement, à partir d’entretiens étudiants, l’utilisation de ChatGPT dans un contexte universitaire. Il vise à identifier les tendances, perceptions et enjeux liés à l’intégration de l’intelligence artificielle dans les pratiques académiques.

Données

Le projet s’appuie sur un corpus d’entretiens qualitatifs menés auprès d’étudiants sur leur usage de ChatGPT. Ce corpus, une fois transcrit et préparé, a été segmenté en lots afin de permettre une analyse efficace par l’IA.

Méthodologie

Deux approches complémentaires ont été employées pour exploiter le corpus :

Codage thématique assisté par IA – Un modèle de langage (LLM) sert au pré-codage thématique des verbatims. Étant donné les limites de contexte du modèle, les entretiens sont découpés en groupes de 5. Chaque lot est codé automatiquement, produisant des fichiers CSV listant les thèmes identifiés avec des extraits associés. Ces résultats sont consolidés puis résumés par l’IA pour obtenir une synthèse thématique globale.

Synthèse automatique par résumés successifs – Chaque entretien est d’abord résumé individuellement pour en extraire les idées principales. Les résumés obtenus sont concaténés et découpés en blocs, puis chaque bloc est résumé à son tour. Ce processus itératif aboutit à une synthèse finale offrant une vue d’ensemble condensée des usages de ChatGPT par les étudiants.

Technologies utilisées

Python – Scripts de traitement de texte en masse (segmentation, concaténation, export CSV).

Modèle de langage (LLM) – Utilisation de Llama pour le codage thématique automatisé et la génération de résumés.

Formats de données – Fichiers CSV pour les codes thématiques, et fichiers texte (.txt) pour les résumés intermédiaires.

Visualisation – Diagramme des codes thématiques (image Codage_ia.jpeg fournie).

Résultats clés

Carte des codes thématiques identifiés. Ce schéma illustre la structure des principaux thèmes évoqués par les étudiants au sujet de ChatGPT. L’analyse fait ressortir plusieurs thématiques clés, notamment :

Stratégies de vérification des réponses.

Fiabilité perçue des sources.

Gains de productivité et limites pour l’apprentissage.

Autonomie vs dépendance à l’outil.

Usage responsable de l’IA et questions éthiques.

En somme, si ChatGPT est perçu comme un atout pour gagner du temps et en efficacité, son utilisation soulève aussi des questions de confiance et d’éthique. Les deux méthodes d’analyse offrent des éclairages complémentaires : l’une ancre l’étude dans le détail des discours, l’autre fournit une vue d’ensemble synthétique.
