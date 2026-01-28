# Scénario de Démo - Customer 360 + Call Center

## 🎯 Objectif de la Démo

Démontrer comment **Microsoft Fabric** permet de créer une vue 360° des clients en combinant :
- **Données transactionnelles** (achats, commandes)
- **Données conversationnelles** (appels, transcripts)
- **Intelligence artificielle** (analyse de sentiment, PII detection, Fabric Data Agent)

Le tout orchestré via **OneLake** et **Shortcut Transformations** pour un pipeline moderne et sans duplication de données.

---

## 📖 Contexte Business

### L'Entreprise : "RetailTech France"

**RetailTech France** est un e-commerce multi-catégories (électronique, électroménager, meubles, mode, jardin) avec :
- **500 clients actifs** sur 6 mois
- **20 000 commandes** passées
- **80 produits** au catalogue
- **Un call center** avec 25 agents gérant ~3 000 appels

### Problématiques Métier

L'entreprise fait face à plusieurs défis :

1. **Fragmentation des données**
   - Données commerciales dans un système CRM/ERP
   - Transcripts d'appels stockés en fichiers texte (.txt) dans un système de téléphonie
   - Pas de vue unifiée du parcours client

2. **Difficultés d'analyse**
   - Impossible de relier facilement un appel à une commande
   - Sentiment client "enfermé" dans les transcripts texte
   - Reporting manuel et long

3. **Réactivité limitée**
   - Les analystes métier ne peuvent pas interroger les données en langage naturel
   - Il faut des compétences SQL/DAX pour répondre aux questions business

---

## 🎬 Scénario Narratif

### Acte 1 : Le Client Mécontent (Semaine 1)

**Personnage** : Sophie Dubois (`CUST_000123`), cliente "regular"

**Chronologie** :
1. **10 août 2025** : Sophie commande un robot de cuisine (produit `PROD_00025`, catégorie Électroménager) pour 299€
2. **15 août** : La commande passe en statut `in_transit`
3. **18 août** : Livraison prévue, mais le colis n'arrive pas
4. **19 août, 14h30** : Sophie appelle le call center (`CALL_001234`)
   - **Raison** : `retard_livraison`
   - **Agent** : Marie Dupont (junior)
   - **Durée** : 8 minutes
   - **Résolu** : Non (le colis est bloqué)
   - **Satisfaction** : 2/5 (négative)

**Transcript clé** (extrait) :
```
Client: Ma commande devait arriver hier mais rien...
Agent: Je comprends votre frustration. Laissez-moi consulter le statut.
Client: C'est marqué 'en transit' depuis 5 jours.
Agent: Le colis est bloqué en entrepôt. Nous faisons le maximum.
Client: Pas très satisfait mais bon.
```

**Analyse IA du transcript** (via Shortcut Transformation) :
- **Sentiment** : Négatif
- **Motif** : Retard de livraison
- **PII détectée** : email mentionné (`sophie.dubois@example.com` - fictif)
- **Résolution** : Non résolue

---

### Acte 2 : Le Retour Gagnant (Semaine 2)

**Suite de l'histoire** :

5. **20 août** : L'entreprise envoie un email d'excuse + bon de réduction 20%
6. **22 août** : Le robot est enfin livré
7. **25 août** : Sophie rappelle (`CALL_001356`)
   - **Raison** : `question_produit` (comment utiliser une fonction)
   - **Agent** : Thomas Martin (expert)
   - **Durée** : 5 minutes
   - **Résolu** : Oui
   - **Satisfaction** : 4/5 (positive)

8. **2 septembre** : Sophie repasse commande (blender 89€) en utilisant son bon de réduction
   - Elle devient progressivement une cliente fidèle

**Insight métier** : Un client mécontent bien géré peut devenir fidèle. Le lien entre appels et re-achats est critique.

---

### Acte 3 : Le Produit Défectueux (Pattern à Détecter)

**Autre personnage** : Marc Leroy (`CUST_000078`), client "premium"

**Pattern problématique** :

- **5 septembre** : Marc achète un aspirateur robot (`PROD_00012`, Électroménager) à 450€
- **12 septembre** : L'aspirateur tombe en panne
- **12 septembre** : Marc appelle (`CALL_002145`)
  - **Raison** : `panne_produit`
  - **Sentiment** : Très négatif
  - **Satisfaction** : 1/5
  - **Résolu** : Non (délai de réparation 2 semaines)

**Ce qui se passe ensuite** :
- Marc ne recommande plus pendant 2 mois
- Il envisage de changer d'enseigne (churn risk)

**Analyse transversale** (via Data Agent) :
- Le produit `PROD_00012` génère **15 appels pour panne** sur 3 mois
- C'est **3x plus** que la moyenne des produits de sa catégorie
- **Alerte qualité produit** → contacter le fournisseur

---

## 🔍 Questions Métier Illustrées par le Scénario

### 1. Vue Client 360

**Question** : "Donne-moi l'historique complet de Sophie Dubois"

**Réponse attendue** :
- 3 commandes (10 août, 2 sept, 15 oct)
- 2 appels (19 août négatif, 25 août positif)
- Évolution sentiment : Négatif → Positif
- Total dépensé : 687€
- Segment : Regular

**Tables utilisées** : `customers`, `orders`, `calls`, `transcripts`

---

### 2. Impact des Appels sur le Réachat

**Question** : "Est-ce que les clients qui appellent achètent plus ou moins après ?"

**Analyse** :
- Clients avec appels résolus : **+35% de réachat dans les 30 jours**
- Clients avec appels non résolus : **-50% de réachat**
- Clients jamais appelé : baseline

**Insight** : La qualité du service call center impacte directement la rétention.

---

### 3. Produits à Problème

**Question** : "Quels sont les 5 produits qui génèrent le plus d'appels négatifs ?"

**Résultat** :
1. Aspirateur robot (`PROD_00012`) : 15 appels, satisfaction moyenne 1.8
2. Machine à café (`PROD_00033`) : 12 appels, satisfaction moyenne 2.1
3. ...

**Action** : Retirer du catalogue, négocier avec fournisseur, améliorer doc produit.

---

### 4. Performance des Agents

**Question** : "Quel agent a le meilleur taux de résolution sur les réclamations ?"

**Résultat** :
- **Thomas Martin (expert)** : 92% de résolution, satisfaction moyenne 4.3
- **Marie Dupont (junior)** : 65% de résolution, satisfaction moyenne 3.2

**Action** : Formation pour agents juniors, mentorat Thomas → Marie.

---

### 5. Prédiction de Churn

**Question** : "Liste les clients à risque de churn"

**Critères** :
- ≥ 2 appels non résolus dans les 60 derniers jours
- Aucun achat depuis > 45 jours
- Satisfaction moyenne < 2.5

**Résultat** : 23 clients identifiés

**Action** : Campagne de rétention (email personnalisé, bon d'achat).

---

## 🏗️ Architecture Démontrée

### Flux de Données

```
┌─────────────────────────────────────────────────────────┐
│                    SOURCES EXTERNES                     │
│  - CRM/ERP (CSV exports)                                │
│  - Système téléphonie (transcripts .txt)                │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Upload/Sync
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      ONELAKE                            │
│  - Shortcuts vers data/raw/commerce (CSV)               │
│  - Shortcuts vers data/raw/callcenter (CSV + .txt)      │
│  - PAS DE DUPLICATION                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Shortcut Transformations AI
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  LAKEHOUSE (Delta Lake)                 │
│  Tables :                                               │
│   - customers, products, orders, order_lines            │
│   - agents, calls                                       │
│   - transcripts_transformed (avec sentiment, summary)   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Semantic Model
                          ▼
┌─────────────────────────────────────────────────────────┐
│               POWER BI / DATA AGENT                     │
│  - Questions en langage naturel                         │
│  - Dashboards interactifs                               │
│  - Alertes automatiques                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🎤 Points Clés de la Démo (Pitch)

1. **"Tout est dans OneLake"**
   - Un seul lac de données pour commerce + call center
   - Pas de duplication, juste des shortcuts

2. **"L'IA comprend le texte"**
   - Les transcripts .txt deviennent une table queryable
   - Sentiment, motifs, PII détectés automatiquement

3. **"Poser des questions, pas du SQL"**
   - Le Data Agent répond en langage naturel
   - "Qui sont mes clients à risque ?" → réponse instantanée

4. **"Du ticket support au CA"**
   - Relier un appel à une commande en 1 clic
   - Mesurer l'impact du service client sur le revenu

5. **"Données fictives, insights réels"**
   - Démo 100% sécurisée (pas de PII réelle)
   - Patterns business crédibles et transposables

---

## 🚀 Variations du Scénario (pour Q&A)

### Si le public demande : "Et pour un autre secteur ?"

**Banque / Assurance** :
- Remplacer "commandes" par "contrats / sinistres"
- Appels = réclamations, demandes de prêt
- Même logique de Customer 360

**Telecom** :
- Remplacer par "abonnements" et "tickets techniques"
- Appels = support technique, upgrade offre

**Healthcare** :
- Patients au lieu de clients
- Appels = rendez-vous, questions médicales (attention HIPAA/RGPD)

➡️ **Le framework Fabric est universel**, seules les données changent.

---

## 📊 Résultats Attendus de la Démo

Après avoir montré le scénario complet, l'audience doit comprendre :

✅ **OneLake = source unique de vérité** (pas de silos)  
✅ **Shortcuts = modernité sans migration** (connecter sans copier)  
✅ **AI Transformations = valeur immédiate** (texte → insights)  
✅ **Data Agent = démocratisation** (tout le monde peut interroger)  
✅ **Delta Lake = performance** (requêtes rapides sur gros volumes)  

**Call to Action** : "Commencez avec un use case simple (Customer 360), prouvez la valeur, puis scalez."

---

## 🎯 Métriques de Succès de la Démo

- **Temps de setup** : < 30 minutes (avec les fichiers pré-générés)
- **Temps de réponse Data Agent** : < 5 secondes par question
- **Nombre de questions "wow"** : au moins 10/15 qui fonctionnent bien
- **Réaction du public** : "Je peux faire ça sur mes données ?"

---

*Fin du scénario. Voir `questions_demo.md` pour les questions spécifiques à poser au Data Agent.*
