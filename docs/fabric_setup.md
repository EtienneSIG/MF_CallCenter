# Guide de Déploiement - Microsoft Fabric

## 🎯 Objectif

Ce guide décrit **étape par étape** comment déployer la démo Customer 360 + Call Center dans Microsoft Fabric.

**Prérequis** :
- Un compte Microsoft Fabric (trial ou licence)
- Les données générées localement (voir README.md)
- Un workspace Fabric créé

**Durée estimée** : 30-45 minutes

---

## 📋 Vue d'Ensemble du Déploiement

```
Étape 1: Créer un Lakehouse
Étape 2: Uploader les données vers OneLake
Étape 3: Créer des OneLake Shortcuts
Étape 4: Appliquer Shortcut Transformations AI sur les transcripts
Étape 5: Charger les CSV en tables Delta
Étape 6: Créer un Semantic Model
Étape 7: Configurer le Fabric Data Agent
Étape 8: Tester et valider
```

---

## Étape 1 : Créer un Lakehouse

### 1.1 Accéder au Workspace

1. Ouvrir [Microsoft Fabric](https://app.fabric.microsoft.com/)
2. Sélectionner ou créer un workspace (ex: `Demo-Customer360`)
3. Vérifier que vous êtes dans l'expérience **Data Engineering**

### 1.2 Créer le Lakehouse

1. Cliquer sur **+ New** → **Lakehouse**
2. Nom : `Customer360_Lakehouse`
3. Cliquer sur **Create**

✅ **Résultat attendu** : Un Lakehouse vide avec deux sections : **Tables** et **Files**.

---

## Étape 2 : Uploader les Données vers OneLake

### 2.1 Préparer les Données Locales

Sur votre machine locale, les données générées sont dans :
```
data/
├── raw/
│   ├── commerce/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_lines.csv
│   └── callcenter/
│       ├── agents.csv
│       ├── calls.csv
│       └── transcripts_txt/
│           ├── CALL_000001.txt
│           ├── CALL_000002.txt
│           └── ... (3000 fichiers)
```

### 2.2 Upload via l'Interface Fabric

**Option A : Upload direct (pour petits volumes)**

1. Dans le Lakehouse, aller dans **Files**
2. Créer une structure de dossiers :
   - Cliquer sur **Upload** → **Upload folder**
   - Sélectionner `data/raw/commerce`
   - Répéter pour `data/raw/callcenter`

**Option B : Upload via OneLake File Explorer (recommandé)**

1. Installer [OneLake File Explorer](https://www.microsoft.com/en-us/download/details.aspx?id=105222) (Windows uniquement)
2. Ouvrir OneLake File Explorer
3. Naviguer vers votre workspace → `Customer360_Lakehouse` → **Files**
4. Copier-coller les dossiers `commerce/` et `callcenter/` depuis votre explorateur Windows

**Option C : Upload via API/CLI (pour automatisation)**

```bash
# Nécessite azcopy ou un script Azure CLI
azcopy copy "data/raw/*" "https://<onelake-path>/Files/raw/" --recursive
```

✅ **Résultat attendu** : Structure de dossiers visible dans **Files** du Lakehouse.

---

## Étape 3 : Créer des OneLake Shortcuts

### 3.1 Principe des Shortcuts

Les **OneLake Shortcuts** créent des liens symboliques sans duplication de données.
Ils permettent de "monter" des données externes (ADLS, S3, etc.) ou internes (autre Lakehouse).

**Pour cette démo** : On va créer des shortcuts vers les fichiers uploadés (optionnel si déjà dans le Lakehouse, mais utile pour démontrer la fonctionnalité).

### 3.2 Créer un Shortcut (Exemple : CSV Commerce)

1. Dans le Lakehouse, section **Files**
2. Clic droit sur la racine → **New shortcut**
3. Choisir **OneLake** (pour lier des fichiers déjà dans Fabric)
4. Sélectionner :
   - **Workspace** : Demo-Customer360
   - **Item** : Customer360_Lakehouse
   - **Path** : `Files/raw/commerce`
5. Nommer le shortcut : `commerce_data`
6. Cliquer sur **Create**

Répéter pour `callcenter` si vous voulez démontrer plusieurs shortcuts.

> **Note** : Si les fichiers sont déjà dans le Lakehouse, cette étape est conceptuelle pour la démo. 
> Dans un scénario réel, les shortcuts pointeraient vers un storage externe (ADLS Gen2, S3, etc.).

✅ **Résultat attendu** : Icône de shortcut visible dans Files, sans duplication de données.

---

## Étape 4 : Appliquer Shortcut Transformations AI sur les Transcripts

### 4.1 Principe des Shortcut Transformations

**Shortcut Transformations AI** (preview) transforme automatiquement des fichiers non structurés (txt, pdf, images) en tables Delta queryables.

Pour les transcripts `.txt`, Fabric peut extraire :
- **Sentiment** (positif/neutre/négatif)
- **Résumé** (summary du contenu)
- **PII Detection** (emails, téléphones, noms)
- **Topics** (sujets détectés)

### 4.2 Créer une Transformation AI

1. Dans le Lakehouse, aller dans **Files** → `raw/callcenter/transcripts_txt/`
2. Clic droit sur le dossier `transcripts_txt` → **New AI transformation** (ou **Apply AI skills**)
   - Si l'option n'est pas visible, vérifier que la preview est activée dans les paramètres du tenant
3. Configurer la transformation :
   - **Source** : `transcripts_txt/` (tous les .txt)
   - **Destination** : Table Delta `transcripts_transformed`
   - **AI Skills à appliquer** :
     - ✅ Sentiment Analysis
     - ✅ Summarization
     - ✅ PII Detection
     - ✅ Key Phrase Extraction
4. Cliquer sur **Create transformation**

### 4.3 Exécuter la Transformation

1. La transformation se lance automatiquement
2. Suivre le progrès dans le **Monitoring** (Activity pane)
3. Temps estimé : 5-10 minutes pour 3000 fichiers (varie selon la charge Fabric)

✅ **Résultat attendu** : Une nouvelle table Delta `transcripts_transformed` apparaît dans **Tables**.

### 4.4 Vérifier le Schéma de la Table Transformée

Colonnes attendues :
- `call_id` (extrait du nom de fichier ou du contenu)
- `content` (texte complet)
- `summary` (résumé généré)
- `sentiment` (positive/neutral/negative)
- `sentiment_score` (0-1)
- `pii_detected` (liste des PII trouvées)
- `key_phrases` (sujets principaux)
- `_metadata` (informations système)

**Exemple de requête test** :
```sql
SELECT call_id, sentiment, summary, pii_detected
FROM transcripts_transformed
LIMIT 10;
```

> **Troubleshooting** : Si la table n'apparaît pas, rafraîchir le Lakehouse ou vérifier les logs de transformation.

---

## Étape 5 : Charger les CSV en Tables Delta

### 5.1 Créer des Tables depuis les CSV

Pour chaque fichier CSV (`customers.csv`, `products.csv`, etc.), créer une table Delta.

**Méthode A : Via l'interface (pour démo interactive)**

1. Dans **Files**, naviguer vers `raw/commerce/customers.csv`
2. Clic droit → **Load to new table**
3. Configurer :
   - **Table name** : `customers`
   - **Delimiter** : Comma
   - **First row has headers** : ✅ Yes
   - **Infer schema** : ✅ Yes
4. Cliquer sur **Load**

Répéter pour :
- `products` (products.csv)
- `orders` (orders.csv)
- `order_lines` (order_lines.csv)
- `agents` (agents.csv)
- `calls` (calls.csv)

**Méthode B : Via Notebook (pour automatisation)**

Créer un Notebook dans le Lakehouse :

```python
# Notebook: Load CSV to Delta Tables

from pyspark.sql import SparkSession

# Chemins des fichiers
files = {
    "customers": "Files/raw/commerce/customers.csv",
    "products": "Files/raw/commerce/products.csv",
    "orders": "Files/raw/commerce/orders.csv",
    "order_lines": "Files/raw/commerce/order_lines.csv",
    "agents": "Files/raw/callcenter/agents.csv",
    "calls": "Files/raw/callcenter/calls.csv"
}

# Charger chaque CSV en table Delta
for table_name, file_path in files.items():
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)
    print(f"✅ Table {table_name} créée avec {df.count()} lignes")
```

Exécuter le notebook (Ctrl+Enter sur chaque cellule).

✅ **Résultat attendu** : 6 tables Delta + 1 table `transcripts_transformed` = 7 tables au total dans **Tables**.

### 5.2 Vérifier les Types de Données

Quelques vérifications importantes :

```sql
-- Vérifier que les dates sont bien en TIMESTAMP
DESCRIBE customers;
-- Attendu: registration_date TIMESTAMP

DESCRIBE orders;
-- Attendu: order_date TIMESTAMP, delivery_date TIMESTAMP

-- Vérifier les nombres
DESCRIBE order_lines;
-- Attendu: quantity INT, unit_price DECIMAL, total_price DECIMAL
```

Si les types sont incorrects (ex: date en STRING), ajuster avec :

```python
from pyspark.sql.functions import to_timestamp

df = spark.table("orders")
df = df.withColumn("order_date", to_timestamp("order_date", "yyyy-MM-dd HH:mm:ss"))
df.write.format("delta").mode("overwrite").saveAsTable("orders")
```

---

## Étape 6 : Créer un Semantic Model

Le **Semantic Model** (ex-Analysis Services) structure les données pour Power BI et le Data Agent.

### 6.1 Créer le Semantic Model

1. Dans le Lakehouse, cliquer sur **New semantic model** (en haut à droite)
2. Nom : `Customer360_Model`
3. Sélectionner les tables à inclure :
   - ✅ customers
   - ✅ products
   - ✅ orders
   - ✅ order_lines
   - ✅ agents
   - ✅ calls
   - ✅ transcripts_transformed
4. Cliquer sur **Confirm**

### 6.2 Définir les Relations

Ouvrir le Semantic Model et créer les relations :

1. Cliquer sur **Model view** (icône diagramme)
2. Créer les relations suivantes (drag & drop entre tables) :

| Table From | Colonne From | Table To | Colonne To | Cardinalité |
|------------|--------------|----------|------------|-------------|
| `orders` | `customer_id` | `customers` | `customer_id` | Many-to-One |
| `order_lines` | `order_id` | `orders` | `order_id` | Many-to-One |
| `order_lines` | `product_id` | `products` | `product_id` | Many-to-One |
| `calls` | `customer_id` | `customers` | `customer_id` | Many-to-One |
| `calls` | `agent_id` | `agents` | `agent_id` | Many-to-One |
| `calls` | `order_id` | `orders` | `order_id` | Many-to-One (*) |
| `calls` | `product_id` | `products` | `product_id` | Many-to-One (*) |
| `calls` | `call_id` | `transcripts_transformed` | `call_id` | One-to-One |

(*) Ces relations sont "sparse" (beaucoup de NULLs). Configurer comme **Inactive** si nécessaire.

### 6.3 Créer des Mesures DAX

Dans le Semantic Model, aller dans **Data view** et créer une **New measure** :

```dax
// Mesures Commerce
Total Orders = COUNTROWS(orders)

Total Revenue = 
SUMX(
    order_lines,
    order_lines[quantity] * order_lines[unit_price] * (1 - order_lines[discount])
)

Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

// Mesures Call Center
Total Calls = COUNTROWS(calls)

Avg Satisfaction = AVERAGE(calls[satisfaction])

Resolution Rate = 
DIVIDE(
    COUNTROWS(FILTER(calls, calls[resolved] = 1)),
    [Total Calls]
)

// Mesures combinées
Calls per Customer = 
DIVIDE(
    [Total Calls],
    DISTINCTCOUNT(calls[customer_id])
)

Callers Revenue = 
CALCULATE(
    [Total Revenue],
    FILTER(
        customers,
        COUNTROWS(RELATEDTABLE(calls)) > 0
    )
)
```

### 6.4 Publier le Semantic Model

1. Cliquer sur **File** → **Save**
2. Le modèle est automatiquement publié dans le workspace

✅ **Résultat attendu** : Semantic Model disponible dans le workspace, prêt pour Power BI et Data Agent.

---

## Étape 7 : Configurer le Fabric Data Agent

### 7.1 Activer la Preview Data Agent

1. Aller dans **Settings** (⚙️) → **Tenant settings** → **Admin Portal**
2. Rechercher **Fabric Data Agent** (ou **Copilot for Data**)
3. Activer la preview pour le workspace

### 7.2 Créer le Data Agent

1. Dans le workspace, cliquer sur **+ New** → **Data Agent** (ou **Copilot**)
2. Nom : `Customer360_Agent`
3. Sélectionner la source :
   - **Type** : Semantic Model
   - **Source** : `Customer360_Model`
4. Cliquer sur **Create**

### 7.3 Configurer les Instructions (System Prompt)

1. Ouvrir le Data Agent
2. Aller dans **Settings** → **Instructions**
3. Coller le contenu de [`data_agent_instructions.md`](data_agent_instructions.md) (voir Étape 8)
4. Sauvegarder

### 7.4 Tester le Data Agent

Poser une première question :
```
Combien de clients avons-nous au total ?
```

Réponse attendue : `500 clients`

Si la réponse est correcte ✅, passer à l'étape 8.

Si la réponse est incorrecte ❌ :
- Vérifier que le Semantic Model est bien publié
- Vérifier les relations entre tables
- Vérifier que les instructions sont bien configurées

---

## Étape 8 : Tester et Valider

### 8.1 Questions de Validation

Poser les questions de [`questions_demo.md`](questions_demo.md) :

1. ✅ Combien de clients avons-nous au total ?
2. ✅ Quelle est la répartition de nos clients par segment ?
3. ✅ Quel est le chiffre d'affaires total généré ?
4. ✅ Quels sont les 5 produits les plus vendus ?
5. ✅ Quel est le taux de satisfaction moyen des appels ?

**Critère de succès** : Au moins 12/15 questions fonctionnent correctement.

### 8.2 Créer un Dashboard Power BI

1. Dans le workspace, cliquer sur **+ New** → **Report**
2. Sélectionner `Customer360_Model` comme source
3. Créer quelques visuels rapides :
   - Card : Total Customers, Total Orders, Total Revenue
   - Donut : Customers by Segment
   - Bar Chart : Top 5 Products
   - Line Chart : Revenue by Month
   - Gauge : Avg Satisfaction
4. Sauvegarder le rapport : `Customer360_Dashboard`

### 8.3 Vérifier les Permissions

Si la démo doit être partagée :
1. Aller dans **Workspace settings** → **Access**
2. Ajouter les viewers/contributors selon les besoins
3. Vérifier que le Semantic Model est partagé (hérite des permissions du workspace)

---

## 🎉 Déploiement Terminé

Vous avez maintenant :
- ✅ Un Lakehouse avec 7 tables Delta
- ✅ Des OneLake Shortcuts (optionnel)
- ✅ Des AI Transformations sur les transcripts
- ✅ Un Semantic Model avec relations et mesures
- ✅ Un Data Agent fonctionnel
- ✅ Un dashboard Power BI de base

**Prochaines étapes** :
- Tester les 15 questions de la démo ([questions_demo.md](questions_demo.md))
- Personnaliser le dashboard Power BI
- Préparer le pitch de présentation ([demo_story.md](demo_story.md))

---

## 🔧 Troubleshooting

### Problème : Les transcripts ne sont pas transformés

**Symptômes** : La table `transcripts_transformed` n'existe pas

**Solutions** :
1. Vérifier que la preview **Shortcut Transformations AI** est activée
2. Vérifier que les fichiers .txt sont bien présents dans `Files/raw/callcenter/transcripts_txt/`
3. Réessayer la transformation manuellement
4. Vérifier les quotas du tenant (limitations preview)

**Alternative** : Créer la table manuellement avec un Notebook :

```python
import os
from pyspark.sql.types import StructType, StructField, StringType

# Lire tous les fichiers .txt
transcripts = []
files_path = "/lakehouse/default/Files/raw/callcenter/transcripts_txt/"

for file in os.listdir(files_path):
    if file.endswith(".txt"):
        with open(os.path.join(files_path, file), "r", encoding="utf-8") as f:
            content = f.read()
            call_id = file.replace(".txt", "")
            # Parsing simple (à améliorer)
            lines = content.split("\n")
            transcripts.append({
                "call_id": call_id,
                "content": content,
                "summary": "Manual summary",  # À générer avec Azure OpenAI si besoin
                "sentiment": "neutral"  # À calculer
            })

# Créer DataFrame et table Delta
schema = StructType([
    StructField("call_id", StringType(), False),
    StructField("content", StringType(), True),
    StructField("summary", StringType(), True),
    StructField("sentiment", StringType(), True)
])

df = spark.createDataFrame(transcripts, schema)
df.write.format("delta").mode("overwrite").saveAsTable("transcripts_transformed")
```

---

### Problème : Le Data Agent ne répond pas correctement

**Symptômes** : Réponses incohérentes ou erreurs

**Solutions** :
1. Vérifier que le Semantic Model est publié (statut "Active")
2. Vérifier les relations entre tables (doivent être correctes)
3. Simplifier la question (utiliser des termes exacts des colonnes)
4. Consulter les instructions du Data Agent et ajuster si nécessaire
5. Vérifier les logs d'erreur dans **Monitoring**

**Exemple** :
- ❌ "Quel est le type de clients ?" (ambigu)
- ✅ "Quelle est la répartition par segment ?" (terme exact : `segment`)

---

### Problème : Erreurs de type de données

**Symptômes** : Les dates sont en texte, les calculs échouent

**Solutions** :
1. Réimporter les CSV avec `inferSchema=True` (Notebook)
2. Caster manuellement les colonnes :

```python
from pyspark.sql.functions import to_timestamp, col

df = spark.table("orders")
df = df.withColumn("order_date", to_timestamp(col("order_date"), "yyyy-MM-dd HH:mm:ss"))
df = df.withColumn("delivery_date", to_timestamp(col("delivery_date"), "yyyy-MM-dd HH:mm:ss"))
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("orders")
```

3. Vérifier l'encodage UTF-8 des CSV (pas de BOM)

---

### Problème : Permissions insuffisantes

**Symptômes** : "Access denied" ou "Not authorized"

**Solutions** :
1. Vérifier que vous êtes **Admin** ou **Member** du workspace
2. Vérifier les permissions sur le Lakehouse (doit être partagé)
3. Vérifier les permissions sur le Semantic Model (hérite du workspace par défaut)

---

## 📚 Ressources Complémentaires

- [Documentation OneLake Shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)
- [AI Transformations in Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/ai-transformations)
- [Fabric Data Agent (Copilot)](https://learn.microsoft.com/en-us/fabric/data-science/data-agent)
- [Semantic Model Best Practices](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)

---

## ✅ Checklist de Déploiement

Cochez au fur et à mesure :

- [ ] Lakehouse créé
- [ ] Données uploadées (CSV + transcripts .txt)
- [ ] OneLake Shortcuts créés (optionnel)
- [ ] AI Transformations appliquées sur transcripts
- [ ] 7 tables Delta créées et vérifiées
- [ ] Semantic Model créé
- [ ] Relations définies dans le modèle
- [ ] Mesures DAX ajoutées
- [ ] Data Agent configuré
- [ ] Instructions du Data Agent ajoutées
- [ ] Questions de test validées (≥12/15)
- [ ] Dashboard Power BI créé
- [ ] Permissions partagées (si nécessaire)

**Si toutes les cases sont cochées, la démo est prête ! 🚀**
