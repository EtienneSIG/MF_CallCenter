# AGENTS.md - Conventions de Développement

## 📋 Contexte du Projet

Ce repository contient une **démo Microsoft Fabric** pour le Customer 360 avec call center :
- OneLake + Shortcuts
- AI Shortcut Transformations (transcripts appels → table queryable)
- Fabric Data Agent (questions en langage naturel)
- Customer 360 : commerce + call center + satisfaction client

**Langue principale** : Français (code en anglais, docs en français)

---

## 🏗️ Structure du Repo

```
Scenario 1- Call center/
├── data/
│   └── raw/
│       ├── commerce/            # CSV commerce (customers, products, orders, order_lines)
│       └── callcenter/          # CSV call center + transcripts .txt
│           └── transcripts_txt/ # Fichiers texte des transcripts
├── src/
│   ├── generate_data.py         # Script principal de génération
│   ├── config.yaml              # Configuration (volumes, distributions)
│   └── lib/                     # Helpers (si nécessaire)
├── docs/
│   ├── schema.md                # Dictionnaire de données (7 tables)
│   ├── demo_story.md            # Scénario "Le Client Fidèle Mécontent"
│   ├── questions_demo.md        # 15 questions Data Agent
│   ├── fabric_setup.md          # Guide déploiement Fabric
│   ├── data_agent_instructions.md
│   └── data_agent_examples.md
├── requirements.txt
├── README.md
└── AGENTS.md                    # Ce fichier
```

---

## 🎯 Conventions de Code

### Noms de Variables et Colonnes

- **Colonnes de tables** : `snake_case` (ex: `customer_id`, `call_duration`)
- **Variables Python** : `snake_case` (ex: `customers_df`, `transcript_metadata`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `CONFIG_FILE`, `SEED`)
- **Noms de classes** : `PascalCase` (ex: `CallCenterDataGenerator`)

### Identifiants Métier

Format standardisé :
- Clients : `CUST_XXXXXX` (6 chiffres)
- Produits : `PROD_XXXXX` (5 chiffres)
- Commandes : `ORD_XXXXXXX` (7 chiffres)
- Lignes de commande : `LINE_XXXXXXXX` (8 chiffres)
- Appels : `CALL_XXXXXX` (6 chiffres)
- Agents : `AGENT_XXX` (3 chiffres)

### Dates et Formats

- **Dates** : ISO 8601 (`YYYY-MM-DD HH:MM:SS`)
- **Encoding** : UTF-8 (tous les fichiers)
- **CSV separator** : virgule (`,`)
- **Decimal separator** : point (`.`)

---

## 🔧 Commandes Fréquentes

### Génération de Données

```powershell
# Générer toutes les données avec config par défaut
cd src
python generate_data.py

# Modifier les volumes : éditer src/config.yaml puis relancer
```

### Vérifications

```powershell
# Vérifier le nombre de lignes générées
Get-ChildItem data\raw\commerce\*.csv | ForEach-Object { 
    Write-Host "$($_.Name): $((Get-Content $_.FullName | Measure-Object -Line).Lines - 1) lignes"
}

Get-ChildItem data\raw\callcenter\*.csv | ForEach-Object { 
    Write-Host "$($_.Name): $((Get-Content $_.FullName | Measure-Object -Line).Lines - 1) lignes"
}

# Compter les transcripts
(Get-ChildItem data\raw\callcenter\transcripts_txt\*.txt | Measure-Object).Count

# Vérifier l'encodage UTF-8
Get-Content data\raw\commerce\customers.csv -Encoding UTF8 | Select-Object -First 5
```

---

## 📝 Guidelines de Modification

### Ajouter une Nouvelle Colonne à une Table

1. Modifier la fonction `generate_XXX()` dans `generate_data.py`
2. Mettre à jour `docs/schema.md` (description de la colonne)
3. Régénérer les données
4. Mettre à jour le Semantic Model dans Fabric (si déployé)

**Exemple** : Ajouter `customer_vip_status` dans `customers`

```python
# Dans generate_customers()
customer = {
    'customer_id': f'CUST_{i+1:06d}',
    # ... autres colonnes
    'vip_status': random.choice(['bronze', 'silver', 'gold', 'platinum']),  # Nouvelle colonne
    'registration_date': ...
}
```

### Ajouter une Nouvelle Raison d'Appel

1. Éditer `src/config.yaml` → `call_reasons`
2. Ajouter la raison avec son poids (distribution)
3. Optionnel : ajouter templates de dialogue dans `_get_dialogue_templates()`
4. Relancer `generate_data.py`

**Exemple** :

```yaml
call_reasons:
  - reason: "demande_remboursement"
    weight: 8
    avg_duration_min: 15
    satisfaction_range: [1, 4]
```

### Modifier les Templates de Transcripts

Les templates sont dans la méthode `_get_dialogue_templates()` de `generate_data.py`.

**Structure** :
- `opening` : Première phrase du client
- `middle_agent` : Réponses intermédiaires agent
- `middle_client` : Réponses intermédiaires client
- `closing_positive` : Clôture si résolu
- `closing_negative` : Clôture si non résolu

Ajouter un nouveau template pour une raison d'appel spécifique.

---

## 🧪 Tests et Validation

### Vérifier la Cohérence Référentielle

```python
# Après génération, lancer ces checks

import pandas as pd

customers_df = pd.read_csv('data/raw/commerce/customers.csv')
orders_df = pd.read_csv('data/raw/commerce/orders.csv')
calls_df = pd.read_csv('data/raw/callcenter/calls.csv')

# Tous les customer_id dans orders existent dans customers ?
assert orders_df['customer_id'].isin(customers_df['customer_id']).all()

# Tous les customer_id dans calls existent dans customers ?
assert calls_df['customer_id'].isin(customers_df['customer_id']).all()

print("✅ Cohérence référentielle OK")
```

### Vérifier les Distributions

```python
# Distribution des segments
print(customers_df['segment'].value_counts(normalize=True))
# Attendu : premium ~15%, regular ~60%, occasional ~25%

# Distribution des raisons d'appel
print(calls_df['reason'].value_counts(normalize=True))
# Attendu : retard_livraison ~30%, panne_produit ~20%, etc.

# CSAT moyen
print(f"CSAT moyen: {calls_df['satisfaction_score'].mean():.2f}/5")
# Attendu : ~3.5-4.0
```

---

## 🚨 Erreurs Fréquentes et Solutions

### Erreur : `UnicodeDecodeError` lors de la lecture des CSV

**Cause** : Encodage incorrect (BOM ou non UTF-8)

**Solution** :
```python
# Forcer UTF-8 sans BOM
df.to_csv(filepath, index=False, encoding='utf-8')
```

### Erreur : Les dates sont en STRING dans Fabric

**Cause** : Inférence de schéma incorrecte

**Solution** : Caster manuellement
```python
from pyspark.sql.functions import to_timestamp
df = df.withColumn("call_start", to_timestamp("call_start", "yyyy-MM-dd HH:mm:ss"))
```

### Erreur : Transcripts vides ou mal formatés

**Cause** : Problème dans `generate_transcript_text()`

**Solution** : Vérifier que :
- Les templates retournent bien des listes de strings
- Le `\n".join(lines)` fonctionne
- L'encodage UTF-8 est préservé dans l'écriture

### Erreur : Relations cassées dans Semantic Model

**Cause** : FK orphelines ou colonnes mal nommées

**Solution** :
- Vérifier que tous les customer_id dans calls/orders existent dans customers
- Vérifier que tous les agent_id existent dans agents
- Revalider les noms de colonnes (snake_case strict)

---

## 📚 Documentation à Maintenir

### Après Modification de `generate_data.py`

1. Mettre à jour `docs/schema.md` si colonnes changées
2. Mettre à jour `README.md` si volumes changés
3. Mettre à jour `docs/data_agent_examples.md` si nouvelles métriques

### Après Modification de `config.yaml`

1. Documenter les nouveaux paramètres dans `README.md`
2. Mettre à jour les valeurs par défaut dans `docs/fabric_setup.md`

---

## 🎨 Suggestions d'Extension

### Idées pour Améliorer la Démo

1. **Ajouter sentiment analysis** : Score de sentiment par transcript (via AI)
2. **Ajouter email support** : Table `email_tickets` avec threads de conversation
3. **Chatbot transcripts** : Ajouter canal "chat" avec conversations automatisées
4. **Prédiction churn** : Score ML basé sur appels négatifs + absence d'achats
5. **Voice analytics** : Métadonnées audio (ton, vitesse de parole, interruptions)

### Nouvelles Tables Possibles

```python
# Table : email_tickets
{
    'ticket_id': 'TICKET_XXXXXX',
    'customer_id': 'CUST_XXXXXX',
    'subject': 'Réclamation livraison',
    'status': 'open|resolved|closed',
    'created_at': datetime,
    'resolved_at': datetime,
    'satisfaction_score': int
}

# Table : chat_sessions
{
    'session_id': 'CHAT_XXXXXX',
    'customer_id': 'CUST_XXXXXX',
    'is_bot': bool,
    'messages_count': int,
    'duration_sec': int,
    'resolved': bool
}
```

---

## 🔐 Sécurité et Conformité

### PII (Personally Identifiable Information)

**Toutes les PII dans ce repo sont FICTIVES** :
- Emails : générés par Faker (`@example.com`)
- Téléphones : générés par Faker (formats français fictifs)
- Noms : générés par Faker (noms communs français)

**Redaction dans les transcripts** :
- Les PII détectées par AI Transformations sont marquées pour démo
- Pas de vraie PII à redacter (tout est synthétique)

### RGPD / GDPR

**Ce dataset ne contient AUCUNE donnée réelle**, donc :
- ✅ Pas de consentement requis (données synthétiques)
- ✅ Pas de droit à l'oubli (clients fictifs)
- ✅ Utilisable librement pour formation/démo

**⚠️ ATTENTION** : Ne jamais utiliser de vraies données clients dans ce repo.

---

## 🤖 Utilisation de Copilot sur ce Repo

### Questions Fréquentes à Poser

**Génération de code** :
- "Ajoute une colonne `preferred_language` dans customers (fr, en, de)"
- "Crée une fonction pour générer des emails de support (similaire aux transcripts)"
- "Ajoute un template de dialogue pour la raison 'demande_facture'"

**Modification de config** :
- "Change les volumes pour avoir 5000 clients et 10000 appels"
- "Ajoute une nouvelle catégorie de produit 'Services' avec 10 produits"

**Debugging** :
- "Pourquoi les CSAT sont tous > 4 ?"
- "Comment corriger les erreurs d'encodage UTF-8 dans les transcripts ?"

**Documentation** :
- "Génère un exemple de requête SQL pour trouver les clients insatisfaits"
- "Ajoute un diagramme de funnel client dans demo_story.md"

### Prompts Efficaces

✅ **Bon prompt** :
> "Dans generate_data.py, ajoute une colonne 'callback_requested' (boolean) dans calls. Corrélation : 80% si satisfaction <= 2, 10% sinon."

❌ **Prompt vague** :
> "Ajoute une colonne callback"

### Contexte à Fournir

Lorsque vous posez une question à Copilot, mentionner :
- Le fichier concerné (`generate_data.py`, `config.yaml`, etc.)
- Le type de modification (ajout, suppression, refactoring)
- Les contraintes (format, distribution, cohérence)

---

## 🧮 Métriques Clés de Référence

### CSAT (Customer Satisfaction)

**Formule** :
```
CSAT = AVG(satisfaction_score) / 5 × 100%
```

**Objectifs** :
- Global : ≥ 80%
- Par agent : ≥ 75%
- Par raison : variable selon criticité

---

### FCR (First Call Resolution)

**Formule** :
```
FCR = Appels résolus au premier contact / Total appels
```

**Objectif** : ≥ 70%

---

### AHT (Average Handle Time)

**Formule** :
```
AHT = AVG(call_duration_min)
```

**Objectifs** :
- Support technique : 12-15 min
- Facturation : 8-10 min
- Réclamation : 15-20 min

---

### Repeat Call Rate

**Formule** :
```
Repeat Calls = Clients avec 2+ appels même raison / Total clients
```

**Objectif** : ≤ 10%

---

## ✅ Checklist avant Commit

Avant de commit des modifications :

- [ ] Code formaté (PEP8 pour Python)
- [ ] `generate_data.py` s'exécute sans erreur
- [ ] Données générées testées (volumes corrects, FK cohérentes)
- [ ] `docs/schema.md` mis à jour si schéma changé
- [ ] `README.md` mis à jour si volumes/features changés
- [ ] Pas de données réelles ajoutées (PII fictives uniquement)
- [ ] Encodage UTF-8 vérifié sur tous les fichiers
- [ ] Config YAML valide (pas d'erreur de syntaxe)
- [ ] Métriques cohérentes (CSAT ≤ 5, durées > 0, etc.)

---

## 📞 Support

Pour questions techniques sur le code :
- Ouvrir une issue GitHub
- Utiliser Copilot Chat avec contexte du fichier

Pour questions sur Microsoft Fabric :
- Consulter [`docs/fabric_setup.md`](docs/fabric_setup.md)
- Voir la [documentation officielle](https://learn.microsoft.com/en-us/fabric/)

Pour questions sur les métriques call center :
- Consulter `docs/data_agent_instructions.md` (formules CSAT, FCR, AHT)

---

**Happy coding! 🚀**

*Ces instructions sont optimisées pour GitHub Copilot et Copilot Chat dans le contexte call center / customer service.*
