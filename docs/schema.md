# Schéma de données - Customer 360 + Call Center

## Vue d'ensemble

Ce schéma décrit toutes les tables de données pour la démo Microsoft Fabric.
Les données sont organisées en deux domaines principaux :
- **Commerce** : données transactionnelles (clients, produits, commandes)
- **Call Center** : données de support client (appels, agents, transcripts)

## Diagramme relationnel

```
┌─────────────┐         ┌─────────────┐
│  CUSTOMERS  │────┬───▶│   ORDERS    │
└─────────────┘    │    └─────────────┘
                   │           │
                   │           │
                   │           ▼
                   │    ┌─────────────┐         ┌─────────────┐
                   │    │ ORDER_LINES │────────▶│  PRODUCTS   │
                   │    └─────────────┘         └─────────────┘
                   │
                   │
                   │    ┌─────────────┐         ┌─────────────┐
                   └───▶│    CALLS    │────────▶│   AGENTS    │
                        └─────────────┘         └─────────────┘
                               │
                               │
                               ▼
                        ┌─────────────┐
                        │ TRANSCRIPTS │
                        │   (.txt)    │
                        └─────────────┘
```

---

## Tables Commerce

### 1. `customers`

Table des clients avec informations personnelles et segmentation.

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `customer_id` | VARCHAR(20) | Identifiant unique du client | **PK**, format `CUST_XXXXXX` |
| `first_name` | VARCHAR(100) | Prénom | NOT NULL |
| `last_name` | VARCHAR(100) | Nom | NOT NULL |
| `email` | VARCHAR(200) | Adresse email | NOT NULL, fictive |
| `phone` | VARCHAR(20) | Numéro de téléphone | Fictif |
| `address` | VARCHAR(300) | Adresse postale | |
| `city` | VARCHAR(100) | Ville | |
| `postal_code` | VARCHAR(10) | Code postal | |
| `country` | VARCHAR(50) | Pays | Toujours 'France' |
| `segment` | VARCHAR(20) | Segment client | `premium`, `regular`, `occasional` |
| `registration_date` | DATETIME | Date d'inscription | Format ISO 8601 |
| `loyalty_points` | INTEGER | Points de fidélité | 0 pour occasional |

**Cardinalité** : 500 lignes

**Index recommandés** :
- `customer_id` (PK)
- `segment`
- `email`

---

### 2. `products`

Catalogue de produits avec prix et catégories.

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `product_id` | VARCHAR(20) | Identifiant unique du produit | **PK**, format `PROD_XXXXX` |
| `product_name` | VARCHAR(200) | Nom du produit | NOT NULL |
| `category` | VARCHAR(50) | Catégorie | NOT NULL |
| `price` | DECIMAL(10,2) | Prix unitaire (€) | > 0 |
| `stock_quantity` | INTEGER | Quantité en stock | >= 0 |
| `supplier` | VARCHAR(200) | Fournisseur | |
| `failure_rate` | DECIMAL(3,2) | Taux de panne (0-1) | Méta-donnée pour simulation |

**Cardinalité** : 80 lignes

**Catégories** :
- Électronique (25 produits)
- Électroménager (20 produits)
- Meubles (15 produits)
- Mode (15 produits)
- Jardin (5 produits)

**Index recommandés** :
- `product_id` (PK)
- `category`

---

### 3. `orders`

Commandes passées par les clients.

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `order_id` | VARCHAR(20) | Identifiant unique de la commande | **PK**, format `ORD_XXXXXXX` |
| `customer_id` | VARCHAR(20) | Client ayant passé la commande | **FK** → `customers.customer_id` |
| `order_date` | DATETIME | Date et heure de la commande | NOT NULL, ISO 8601 |
| `status` | VARCHAR(20) | Statut de la commande | `delivered`, `in_transit`, `processing`, `cancelled` |
| `delivery_date` | DATETIME | Date de livraison (si applicable) | Peut être NULL |
| `shipping_address` | VARCHAR(500) | Adresse de livraison | |
| `payment_method` | VARCHAR(20) | Méthode de paiement | `card`, `paypal`, `bank_transfer` |
| `shipping_cost` | DECIMAL(10,2) | Frais de port (€) | |

**Cardinalité** : 20 000 lignes

**Relations** :
- `customer_id` → `customers.customer_id` (N:1)

**Distribution des statuts** :
- `delivered`: 75%
- `in_transit`: 15%
- `processing`: 8%
- `cancelled`: 2%

**Index recommandés** :
- `order_id` (PK)
- `customer_id` (FK)
- `order_date`
- `status`

---

### 4. `order_lines`

Lignes de détail des commandes (produits commandés).

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `line_id` | VARCHAR(20) | Identifiant unique de la ligne | **PK**, format `LINE_XXXXXXXX` |
| `order_id` | VARCHAR(20) | Commande associée | **FK** → `orders.order_id` |
| `product_id` | VARCHAR(20) | Produit commandé | **FK** → `products.product_id` |
| `quantity` | INTEGER | Quantité commandée | > 0 |
| `unit_price` | DECIMAL(10,2) | Prix unitaire au moment de la commande (€) | > 0 |
| `discount` | DECIMAL(3,2) | Remise appliquée (0-1) | 0 = pas de remise |
| `total_price` | DECIMAL(10,2) | Prix total de la ligne (€) | `quantity * unit_price * (1 - discount)` |

**Cardinalité** : ~60 000 lignes (3 lignes/commande en moyenne)

**Relations** :
- `order_id` → `orders.order_id` (N:1)
- `product_id` → `products.product_id` (N:1)

**Index recommandés** :
- `line_id` (PK)
- `order_id` (FK)
- `product_id` (FK)

---

## Tables Call Center

### 5. `agents`

Agents du call center.

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `agent_id` | VARCHAR(20) | Identifiant unique de l'agent | **PK**, format `AGENT_XXX` |
| `first_name` | VARCHAR(100) | Prénom | NOT NULL |
| `last_name` | VARCHAR(100) | Nom | NOT NULL |
| `email` | VARCHAR(200) | Email professionnel | Fictif |
| `hire_date` | DATETIME | Date d'embauche | ISO 8601 |
| `experience_level` | VARCHAR(20) | Niveau d'expérience | `junior`, `senior`, `expert` |
| `languages` | VARCHAR(50) | Langues parlées (séparées par virgule) | Ex: `fr,en` |

**Cardinalité** : 25 lignes

**Distribution expérience** :
- Junior (0-2 ans): 40%
- Senior (3-7 ans): 40%
- Expert (8+ ans): 20%

**Index recommandés** :
- `agent_id` (PK)
- `experience_level`

---

### 6. `calls`

Faits d'appels au call center.

| Colonne | Type | Description | Contraintes |
|---------|------|-------------|-------------|
| `call_id` | VARCHAR(20) | Identifiant unique de l'appel | **PK**, format `CALL_XXXXXX` |
| `customer_id` | VARCHAR(20) | Client ayant appelé | **FK** → `customers.customer_id` |
| `agent_id` | VARCHAR(20) | Agent ayant traité l'appel | **FK** → `agents.agent_id` |
| `call_date` | DATETIME | Date et heure de l'appel | NOT NULL, ISO 8601 |
| `channel` | VARCHAR(20) | Canal de communication | `phone`, `email`, `chat` |
| `reason` | VARCHAR(50) | Raison de l'appel | Voir liste ci-dessous |
| `duration_seconds` | INTEGER | Durée de l'appel (secondes) | >= 0 |
| `satisfaction` | INTEGER | Score de satisfaction (1-5) | 1 = très insatisfait, 5 = très satisfait |
| `resolved` | INTEGER | Appel résolu ? | 0 = non, 1 = oui |
| `order_id` | VARCHAR(20) | Commande associée (optionnel) | **FK** → `orders.order_id`, peut être vide |
| `product_id` | VARCHAR(20) | Produit concerné (optionnel) | **FK** → `products.product_id`, peut être vide |

**Cardinalité** : 3 000 lignes

**Relations** :
- `customer_id` → `customers.customer_id` (N:1)
- `agent_id` → `agents.agent_id` (N:1)
- `order_id` → `orders.order_id` (N:1, optionnel)
- `product_id` → `products.product_id` (N:1, optionnel)

**Raisons d'appel** (avec distribution) :
- `retard_livraison`: 30%
- `remboursement`: 15%
- `panne_produit`: 20%
- `changement_info`: 10%
- `question_produit`: 15%
- `autre`: 10%

**Canaux** :
- `phone`: 70%
- `email`: 20%
- `chat`: 10%

**Index recommandés** :
- `call_id` (PK)
- `customer_id` (FK)
- `agent_id` (FK)
- `call_date`
- `reason`
- `satisfaction`
- `order_id` (FK, sparse)

---

### 7. `transcripts` (fichiers .txt)

Transcriptions textuelles des appels.

**Format** : Un fichier `.txt` par appel, nommé `{call_id}.txt`

**Structure du fichier** :
```
CALL_ID: CALL_000123
CUSTOMER_ID: CUST_000456
DATE: 2025-12-15 14:30:00
PRODUCT: PROD_00042
REASON: retard_livraison

=== TRANSCRIPT ===

Agent: Bonjour, Marie Dupont à votre service. Comment puis-je vous aider ?
Client: Bonjour, j'ai commandé il y a une semaine et je n'ai toujours rien reçu.
Agent: Je vérifie cela pour vous. Pouvez-vous me donner votre numéro de commande ?
Client: C'est marqué 'en transit' depuis 5 jours.
...
```

**Cardinalité** : 3 000 fichiers .txt

**Contenu** :
- 5 lignes d'en-tête (métadonnées clés/valeurs)
- Ligne de séparation
- Dialogue alternant Agent/Client (6 échanges en moyenne)
- Peut contenir de fausses PII (email, téléphone fictifs) pour démo de redaction

**Relation logique** :
- Nom du fichier correspond à `calls.call_id`
- Métadonnées en en-tête permettent le parsing

---

## Clés de jointure importantes

### Lien Commerce ↔ Call Center

**Question métier** : Quels clients qui ont commandé ont ensuite appelé le support ?

```sql
SELECT c.customer_id, c.first_name, c.last_name, 
       o.order_id, o.order_date,
       ca.call_id, ca.call_date, ca.reason
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN calls ca ON c.customer_id = ca.customer_id
WHERE ca.call_date BETWEEN o.order_date AND DATEADD(day, 14, o.order_date)
```

### Lien Produits ↔ Appels

**Question métier** : Quels produits génèrent le plus d'appels de support ?

```sql
SELECT p.product_id, p.product_name, p.category,
       COUNT(ca.call_id) as nb_calls,
       AVG(ca.satisfaction) as avg_satisfaction
FROM products p
JOIN calls ca ON p.product_id = ca.product_id
WHERE ca.reason IN ('panne_produit', 'question_produit')
GROUP BY p.product_id, p.product_name, p.category
ORDER BY nb_calls DESC
```

### Lien Transcripts ↔ Calls

**Question métier** : Analyser le sentiment des conversations pour les appels non résolus

```sql
-- Après transformation AI des transcripts en table Delta
SELECT t.call_id, t.sentiment, t.summary,
       ca.reason, ca.satisfaction, ca.resolved
FROM transcripts_transformed t
JOIN calls ca ON t.call_id = ca.call_id
WHERE ca.resolved = 0
```

---

## Mesures DAX recommandées

Pour le modèle sémantique Power BI / Fabric :

```dax
// Mesures de base
Total Orders = COUNTROWS(orders)
Total Revenue = SUMX(order_lines, order_lines[quantity] * order_lines[unit_price] * (1 - order_lines[discount]))
Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

// Mesures Call Center
Total Calls = COUNTROWS(calls)
Avg Satisfaction = AVERAGE(calls[satisfaction])
Resolution Rate = DIVIDE(COUNTROWS(FILTER(calls, calls[resolved] = 1)), [Total Calls])

// Mesures combinées
Calls per Order = DIVIDE([Total Calls], [Total Orders])
Revenue from Callers = 
    CALCULATE(
        [Total Revenue],
        FILTER(customers, 
            COUNTROWS(RELATEDTABLE(calls)) > 0
        )
    )
```

---

## Notes techniques

### Encodage et formats
- **Encodage** : UTF-8 (tous les fichiers)
- **Séparateur CSV** : virgule (`,`)
- **Dates** : ISO 8601 (`YYYY-MM-DD HH:MM:SS`)
- **Décimales** : point (`.`)
- **Noms de colonnes** : snake_case

### Cohérence référentielle
- Tous les `customer_id` dans `orders` et `calls` existent dans `customers`
- Tous les `product_id` dans `order_lines` existent dans `products`
- Tous les `agent_id` dans `calls` existent dans `agents`
- Les `order_id` et `product_id` dans `calls` peuvent être vides (NULL/empty string)

### Fenêtre temporelle
- **Période** : 6 mois (2025-08-01 → 2026-01-28)
- **Lien temporel Call/Order** : ±14 jours autour de la date de commande

### Seed
- **Seed stable** : 42 (reproductibilité garantie)
