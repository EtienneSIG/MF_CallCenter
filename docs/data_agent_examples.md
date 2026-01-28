# Exemples de Questions pour Fabric Data Agent

## 🎯 Objectif

Ce document fournit **20 exemples de questions** avec les **réponses attendues** pour tester et valider le Fabric Data Agent.

Chaque exemple inclut :
- La question posée
- La réponse attendue (format et contenu)
- Les tables utilisées
- Le type de visualisation suggéré

---

## 📊 Catégorie 1 : Exploration Simple (5 questions)

### 1. Combien de clients avons-nous au total ?

**Réponse attendue** :
> 500 clients au total.
> 
> *Source : table `customers`*

**Tables** : `customers`  
**Visualisation** : Card/KPI  
**Complexité** : ⭐ (très simple)

---

### 2. Quelle est la répartition de nos clients par segment ?

**Réponse attendue** :
> Répartition des clients par segment :
> - Premium : 75 clients (15%)
> - Regular : 300 clients (60%)
> - Occasional : 125 clients (25%)
> 
> *Source : table `customers`, colonne `segment`*

**Tables** : `customers`  
**Visualisation** : Donut chart  
**Complexité** : ⭐ (simple)

---

### 3. Combien de produits avons-nous au catalogue ?

**Réponse attendue** :
> 80 produits répartis en 5 catégories :
> - Électronique : 25 produits
> - Électroménager : 20 produits
> - Meubles : 15 produits
> - Mode : 15 produits
> - Jardin : 5 produits
> 
> *Source : table `products`*

**Tables** : `products`  
**Visualisation** : Bar chart horizontal  
**Complexité** : ⭐ (simple)

---

### 4. Combien de commandes avons-nous traitées depuis août 2025 ?

**Réponse attendue** :
> 20 000 commandes sur la période août 2025 - janvier 2026.
> 
> *Source : table `orders`, filtre sur `order_date`*

**Tables** : `orders`  
**Visualisation** : Card/KPI  
**Complexité** : ⭐ (simple avec filtre temporel)

---

### 5. Combien d'agents travaillent au call center ?

**Réponse attendue** :
> 25 agents au total, répartis par niveau d'expérience :
> - Junior (0-2 ans) : 10 agents (40%)
> - Senior (3-7 ans) : 10 agents (40%)
> - Expert (8+ ans) : 5 agents (20%)
> 
> *Source : table `agents`*

**Tables** : `agents`  
**Visualisation** : Donut chart  
**Complexité** : ⭐ (simple)

---

## 💰 Catégorie 2 : Agrégations Commerce (5 questions)

### 6. Quel est le chiffre d'affaires total généré ?

**Réponse attendue** :
> Chiffre d'affaires total : **~2,4 millions €** sur la période août 2025 - janvier 2026.
> 
> Calculé comme : SUM(quantity × unit_price × (1 - discount)) depuis `order_lines`.
> 
> *Source : table `order_lines`*

**Tables** : `order_lines`  
**Visualisation** : Card/KPI  
**Complexité** : ⭐⭐ (calcul multi-colonnes)

---

### 7. Quel est le panier moyen par commande ?

**Réponse attendue** :
> Panier moyen : **~120€** par commande.
> 
> Calculé comme : Total revenue (2,4M€) / Nombre de commandes (20 000).
> 
> *Source : tables `orders` et `order_lines`*

**Tables** : `orders`, `order_lines`  
**Visualisation** : Card/KPI  
**Complexité** : ⭐⭐ (jointure + division)

---

### 8. Quels sont les 5 produits les plus vendus en quantité ?

**Réponse attendue** :
> Top 5 produits les plus vendus :
> 1. Smartphone XYZ (PROD_00001) : 1 234 unités
> 2. Cafetière ABC (PROD_00033) : 987 unités
> 3. Chaise de bureau (PROD_00045) : 876 unités
> 4. T-shirt Classic (PROD_00067) : 765 unités
> 5. Tondeuse Jardin (PROD_00078) : 654 unités
> 
> *Source : jointure `products` et `order_lines`, agrégation par produit, tri DESC*

**Tables** : `products`, `order_lines`  
**Visualisation** : Bar chart horizontal  
**Complexité** : ⭐⭐ (jointure + tri)

---

### 9. Quel est le taux d'annulation des commandes ?

**Réponse attendue** :
> Taux d'annulation : **2%** (400 commandes annulées sur 20 000).
> 
> Statuts des commandes :
> - Delivered : 15 000 (75%)
> - In transit : 3 000 (15%)
> - Processing : 1 600 (8%)
> - Cancelled : 400 (2%)
> 
> *Source : table `orders`, colonne `status`*

**Tables** : `orders`  
**Visualisation** : Donut chart  
**Complexité** : ⭐⭐ (filtre + pourcentage)

---

### 10. Quelle est l'évolution du chiffre d'affaires par mois ?

**Réponse attendue** :
> Évolution mensuelle du CA :
> - Août 2025 : 350 K€
> - Septembre 2025 : 380 K€
> - Octobre 2025 : 420 K€
> - Novembre 2025 : 490 K€ (Black Friday)
> - Décembre 2025 : 510 K€ (Noël)
> - Janvier 2026 : 250 K€ (partiel)
> 
> *Tendance : Hausse progressive avec pics saisonniers.*
> 
> *Source : `order_lines` jointure `orders`, agrégation par mois*

**Tables** : `orders`, `order_lines`  
**Visualisation** : Line chart  
**Complexité** : ⭐⭐⭐ (temporalité + agrégation)

---

## 📞 Catégorie 3 : Call Center Insights (5 questions)

### 11. Combien d'appels avons-nous reçus ce mois-ci ?

**Réponse attendue** :
> **450 appels** en janvier 2026 (mois en cours).
> 
> *Source : table `calls`, filtre sur `call_date` >= 2026-01-01*

**Tables** : `calls`  
**Visualisation** : Card/KPI  
**Complexité** : ⭐ (filtre temporel relatif)

---

### 12. Quel est le taux de satisfaction moyen des appels ?

**Réponse attendue** :
> Satisfaction moyenne : **3.8/5**
> 
> Répartition :
> - Score 5 (très satisfait) : 25%
> - Score 4 : 35%
> - Score 3 : 22%
> - Score 2 : 12%
> - Score 1 (très insatisfait) : 6%
> 
> *Source : table `calls`, colonne `satisfaction`*

**Tables** : `calls`  
**Visualisation** : Gauge + Bar chart  
**Complexité** : ⭐⭐ (moyenne + distribution)

---

### 13. Quelle est la principale raison des appels clients ?

**Réponse attendue** :
> Top 3 raisons d'appel :
> 1. **Retard de livraison** : 900 appels (30%)
> 2. **Panne produit** : 600 appels (20%)
> 3. **Remboursement** : 450 appels (15%)
> 
> *Source : table `calls`, colonne `reason`*

**Tables** : `calls`  
**Visualisation** : Bar chart horizontal  
**Complexité** : ⭐⭐ (agrégation + tri)

---

### 14. Quel est le taux de résolution des appels ?

**Réponse attendue** :
> Taux de résolution : **75%** (2 250 appels résolus sur 3 000).
> 
> Variation par canal :
> - Phone : 78% résolution
> - Email : 70% résolution
> - Chat : 72% résolution
> 
> *Source : table `calls`, colonne `resolved`*

**Tables** : `calls`  
**Visualisation** : Gauge + Table  
**Complexité** : ⭐⭐ (pourcentage + groupby)

---

### 15. Quelle est la durée moyenne d'un appel ?

**Réponse attendue** :
> Durée moyenne : **5 minutes 20 secondes** (320 secondes).
> 
> Variation par raison :
> - Panne produit : 8 min (le plus long)
> - Question produit : 4 min
> - Retard livraison : 6 min
> - Changement info : 3 min (le plus court)
> 
> *Source : table `calls`, colonne `duration_seconds`*

**Tables** : `calls`  
**Visualisation** : Bar chart  
**Complexité** : ⭐⭐ (moyenne + groupby)

---

## 🔗 Catégorie 4 : Analyses Cross-Domain (5 questions)

### 16. Combien de clients ayant commandé ont également appelé le support ?

**Réponse attendue** :
> **380 clients** ont à la fois commandé et appelé le support (76% des clients).
> 
> Répartition :
> - Clients avec commandes uniquement : 95 clients (19%)
> - Clients avec commandes ET appels : 380 clients (76%)
> - Clients ayant appelé sans commander : 25 clients (5%)
> 
> *Source : jointure entre `customers`, `orders` et `calls`*

**Tables** : `customers`, `orders`, `calls`  
**Visualisation** : Venn diagram ou Stacked bar  
**Complexité** : ⭐⭐⭐ (jointures multiples)

---

### 17. Quels produits génèrent le plus d'appels pour panne ?

**Réponse attendue** :
> Top 5 produits générant des appels "panne_produit" :
> 1. **Aspirateur robot (PROD_00012)** : 15 appels (5% des ventes = très élevé)
> 2. **Machine à café (PROD_00033)** : 12 appels
> 3. **Perceuse électrique (PROD_00018)** : 10 appels
> 4. **Mixeur (PROD_00025)** : 8 appels
> 5. **Lampe LED (PROD_00003)** : 7 appels
> 
> ⚠️ **Alerte qualité** : PROD_00012 a un taux de panne 3x supérieur à la moyenne.
> 
> *Source : `calls` (filtre reason='panne_produit') jointure `products`*

**Tables** : `calls`, `products`  
**Visualisation** : Bar chart + warning icon  
**Complexité** : ⭐⭐⭐ (jointure + filtre + benchmark)

---

### 18. Quel est le délai moyen entre une commande et un appel pour retard de livraison ?

**Réponse attendue** :
> Délai moyen : **8 jours** entre la commande et l'appel pour retard.
> 
> Répartition :
> - 3-5 jours : 20% (clients impatients)
> - 6-10 jours : 50% (délai normal)
> - 11-14 jours : 30% (retard avéré)
> 
> *Source : jointure `orders` et `calls` (filtre reason='retard_livraison'), calcul DATEDIFF*

**Tables** : `orders`, `calls`  
**Visualisation** : Histogram  
**Complexité** : ⭐⭐⭐⭐ (jointure temporelle + calcul date)

---

### 19. Les clients qui appellent dépensent-ils plus ou moins que les autres ?

**Réponse attendue** :
> **Clients ayant appelé** :
> - CA moyen par client : 550€
> - Panier moyen : 135€
> - Nombre moyen de commandes : 4.1
> 
> **Clients n'ayant jamais appelé** :
> - CA moyen par client : 480€
> - Panier moyen : 120€
> - Nombre moyen de commandes : 4.0
> 
> **Insight** : Les clients qui appellent dépensent **+15%** (ils sont plus engagés, pas forcément insatisfaits).
> 
> *Source : segmentation des clients selon présence dans `calls`, agrégation sur `orders` et `order_lines`*

**Tables** : `customers`, `calls`, `orders`, `order_lines`  
**Visualisation** : Comparison bar chart  
**Complexité** : ⭐⭐⭐⭐ (segmentation + comparaison)

---

### 20. Quels clients n'ont pas racheté après un appel non résolu ?

**Réponse attendue** :
> **67 clients** n'ont pas repassé commande après un appel non résolu.
> 
> Profil type :
> - Segment : 60% regular, 30% occasional, 10% premium
> - Raison d'appel : 45% panne produit, 35% remboursement, 20% retard
> - Satisfaction moyenne : 1.9/5
> 
> **Risque de churn élevé** → Campagne de rétention recommandée (bon d'achat, email personnalisé).
> 
> *Source : `calls` (filtre resolved=0) jointure `customers` et `orders`, exclusion des clients ayant commandé après la date de l'appel*

**Tables** : `calls`, `customers`, `orders`  
**Visualisation** : Table avec alerte + Donut pour segments  
**Complexité** : ⭐⭐⭐⭐⭐ (logique temporelle complexe)

---

## 🎯 Questions Bonus (pour aller plus loin)

### B1. Quel agent a le meilleur taux de résolution et combien d'appels a-t-il traité ?

**Réponse attendue** :
> **Thomas Martin (AGENT_007)** :
> - Taux de résolution : 92%
> - Appels traités : 234
> - Satisfaction moyenne : 4.3/5
> - Expérience : Expert (10 ans)
> 
> Top 3 agents :
> 1. Thomas Martin : 92% (234 appels)
> 2. Sophie Leroy : 88% (198 appels)
> 3. Pierre Dubois : 85% (267 appels)
> 
> *Source : `agents` jointure `calls`, agrégation par agent*

**Tables** : `agents`, `calls`  
**Visualisation** : Leaderboard table  
**Complexité** : ⭐⭐⭐ (jointure + ranking)

---

### B2. Affiche-moi l'évolution du nombre d'appels par semaine

**Réponse attendue** :
> [Graphique line chart avec évolution hebdomadaire]
> 
> Tendance : Pic d'appels en semaine 47 (Black Friday) et semaine 51 (Noël).
> Moyenne : 115 appels/semaine.
> 
> *Source : `calls`, agrégation par semaine*

**Tables** : `calls`  
**Visualisation** : Line chart  
**Complexité** : ⭐⭐⭐ (temporalité)

---

### B3. Quels clients premium ont dépensé plus de 2000€ ?

**Réponse attendue** :
> **12 clients premium** ont dépensé plus de 2000€ :
> 
> 1. Jean Dupont (CUST_000042) : 3 450€
> 2. Marie Martin (CUST_000078) : 2 890€
> 3. ...
> 
> *Ils représentent 16% des clients premium et 22% du CA premium.*
> 
> *Source : `customers` (filtre segment='premium') jointure `orders` et `order_lines`, agrégation par client*

**Tables** : `customers`, `orders`, `order_lines`  
**Visualisation** : Table  
**Complexité** : ⭐⭐⭐ (filtres multiples + seuil)

---

## 📋 Guide d'Utilisation

### Comment Tester ces Questions

1. **Ordre recommandé** : Commencer par les questions simples (catégorie 1), puis augmenter la complexité
2. **Validation** : Vérifier que la réponse est cohérente (chiffres dans les bons ordres de grandeur)
3. **Flexibilité** : Reformuler si la première tentative échoue (utiliser termes exacts des colonnes)

### Critères de Succès

| Niveau | Questions réussies | Commentaire |
|--------|-------------------|-------------|
| ⭐ Basic | 15+/20 | Fonctionnel pour démo |
| ⭐⭐ Good | 17+/20 | Très bon niveau |
| ⭐⭐⭐ Excellent | 19+/20 | Production-ready |

### Troubleshooting

| Problème | Solution |
|----------|----------|
| Réponse incorrecte | Vérifier les relations dans le Semantic Model |
| Timeout | Filtrer sur période plus courte |
| "Je ne peux pas répondre" | Reformuler avec termes exacts des colonnes |
| Graphique non généré | Demander explicitement "en graphique" |

---

## 🎨 Variations de Questions (pour Improvisation)

Vous pouvez varier les questions en changeant :
- **La période** : "ce mois-ci", "le trimestre dernier", "depuis début 2025"
- **Le segment** : "clients premium", "clients occasional"
- **Le top N** : "top 3", "top 10", "les 5 pires"
- **Le canal** : "par téléphone", "par email"
- **La catégorie** : "produits électronique", "meubles"

**Exemple de variations** :
- "Quel est le CA des clients premium ce trimestre ?"
- "Quels sont les 10 produits Mode les plus vendus ?"
- "Combien d'appels par chat en décembre ?"

---

*Ces 20 exemples couvrent l'ensemble des capacités attendues du Fabric Data Agent pour cette démo.*
