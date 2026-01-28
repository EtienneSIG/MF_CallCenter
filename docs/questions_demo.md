# Questions de Démo - Fabric Data Agent

## 🎯 Objectif

Cette liste contient **15 questions "wow effect"** à poser au **Fabric Data Agent** pendant la démo.
Chaque question illustre une capacité différente et crée un impact auprès de l'audience.

Les questions sont organisées par **niveau de complexité** et **cas d'usage métier**.

---

## ✅ Questions Niveau 1 : Exploration Simple

### 1. Combien de clients avons-nous au total ?

**Attendu** :
- Réponse : "500 clients"
- Tables utilisées : `customers`
- Graphique suggéré : Card / KPI

**Pourquoi c'est "wow"** : Question ultra-simple, réponse instantanée. Démo que le Data Agent comprend le français naturel.

---

### 2. Quelle est la répartition de nos clients par segment ?

**Attendu** :
- Réponse : 
  - Premium: 75 clients (15%)
  - Regular: 300 clients (60%)
  - Occasional: 125 clients (25%)
- Tables utilisées : `customers`
- Graphique suggéré : Donut chart

**Pourquoi c'est "wow"** : Le Data Agent propose une visualisation pertinente.

---

### 3. Combien de commandes avons-nous traitées depuis août 2025 ?

**Attendu** :
- Réponse : "20 000 commandes"
- Tables utilisées : `orders`
- Filtre : `order_date >= '2025-08-01'`

**Pourquoi c'est "wow"** : Comprend les dates et les périodes en langage naturel.

---

## 📊 Questions Niveau 2 : Agrégations et Calculs

### 4. Quel est le chiffre d'affaires total généré ?

**Attendu** :
- Réponse : ~X million d'euros (calculé depuis `order_lines`)
- Tables utilisées : `order_lines`
- Calcul : `SUM(quantity * unit_price * (1 - discount))`

**Pourquoi c'est "wow"** : Calcul automatique multi-colonnes, pas besoin d'écrire la formule.

---

### 5. Quel est le panier moyen par commande ?

**Attendu** :
- Réponse : ~XXX€
- Tables utilisées : `orders`, `order_lines`
- Calcul : Total revenue / nombre de commandes

**Pourquoi c'est "wow"** : Jointure implicite entre tables.

---

### 6. Quels sont les 5 produits les plus vendus ?

**Attendu** :
- Réponse : Liste de 5 produits avec quantités vendues
- Tables utilisées : `products`, `order_lines`
- Tri : `ORDER BY SUM(quantity) DESC LIMIT 5`
- Graphique suggéré : Bar chart

**Pourquoi c'est "wow"** : Ranking automatique, suggestion de visualisation.

---

## 📞 Questions Niveau 3 : Call Center Insights

### 7. Combien d'appels avons-nous reçus ce mois-ci ?

**Attendu** :
- Réponse : XXX appels (filtré sur janvier 2026)
- Tables utilisées : `calls`
- Filtre temporel intelligent (comprend "ce mois-ci")

**Pourquoi c'est "wow"** : Contexte temporel relatif ("ce mois-ci" = janvier 2026).

---

### 8. Quel est le taux de satisfaction moyen des appels ?

**Attendu** :
- Réponse : 3.8/5 (moyenne de `satisfaction`)
- Tables utilisées : `calls`
- Graphique suggéré : Gauge

**Pourquoi c'est "wow"** : Métrique métier standard, réponse directe.

---

### 9. Quelle est la principale raison des appels clients ?

**Attendu** :
- Réponse : "Retard de livraison (30% des appels)"
- Tables utilisées : `calls`
- Agrégation : `GROUP BY reason ORDER BY COUNT(*) DESC`
- Graphique suggéré : Bar chart horizontal

**Pourquoi c'est "wow"** : Identification automatique du top motif + pourcentage.

---

### 10. Quel est le taux de résolution des appels ?

**Attendu** :
- Réponse : ~75% (calculé depuis `resolved`)
- Tables utilisées : `calls`
- Calcul : `SUM(resolved) / COUNT(*) * 100`

**Pourquoi c'est "wow"** : KPI métier compris et calculé automatiquement.

---

## 🔗 Questions Niveau 4 : Analyse Cross-Domain (Commerce + Call Center)

### 11. Combien de clients ayant commandé ont également appelé le support ?

**Attendu** :
- Réponse : XXX clients
- Tables utilisées : `customers`, `orders`, `calls`
- Jointure : DISTINCT customers ayant au moins 1 order ET au moins 1 call

**Pourquoi c'est "wow"** : Jointure multi-tables complexe résolue automatiquement.

---

### 12. Quels produits génèrent le plus d'appels pour panne ?

**Attendu** :
- Réponse : Top 5 produits avec nombre d'appels "panne_produit"
- Tables utilisées : `products`, `calls`
- Filtre : `reason = 'panne_produit'`
- Graphique suggéré : Bar chart

**Pourquoi c'est "wow"** : Identification de problèmes qualité produit via les appels.

---

### 13. Quel est le délai moyen entre une commande et un appel pour retard de livraison ?

**Attendu** :
- Réponse : ~8 jours (calculé)
- Tables utilisées : `orders`, `calls`
- Calcul : `AVG(DATEDIFF(calls.call_date, orders.order_date))`
- Filtre : `reason = 'retard_livraison'` ET lien order_id

**Pourquoi c'est "wow"** : Calcul temporel complexe entre deux événements.

---

## 🚨 Questions Niveau 5 : Insights Avancés et Prédictifs

### 14. Quels clients n'ont pas racheté après un appel non résolu ?

**Attendu** :
- Réponse : Liste de X clients
- Tables utilisées : `customers`, `calls`, `orders`
- Logique : 
  - Clients ayant un appel avec `resolved = 0`
  - Sans commande après la date de cet appel
- Graphique suggéré : Table avec détails

**Pourquoi c'est "wow"** : Analyse de churn basée sur comportement multi-domaines.

---

### 15. Quel agent a le meilleur taux de résolution et combien d'appels a-t-il traité ?

**Attendu** :
- Réponse : "Thomas Martin (AGENT_007) : 92% de résolution sur 234 appels"
- Tables utilisées : `agents`, `calls`
- Calcul : `SUM(resolved) / COUNT(*)` par agent, tri DESC
- Graphique suggéré : Table leaderboard

**Pourquoi c'est "wow"** : Performance individuelle, ranking, métrique composite.

---

## 🎨 Questions Bonus (Variantes pour Impact)

### B1. Affiche-moi l'évolution du chiffre d'affaires par mois

**Attendu** : Line chart avec CA mensuel (août 2025 → janvier 2026)

**Pourquoi c'est "wow"** : Temporalité + tendance visuelle.

---

### B2. Quels clients premium ont dépensé plus de 2000€ ?

**Attendu** : Liste de clients avec total dépensé

**Pourquoi c'est "wow"** : Filtres multiples (segment + seuil) + agrégation.

---

### B3. Quel est le produit le plus cher jamais commandé ?

**Attendu** : Nom du produit + prix

**Pourquoi c'est "wow"** : Superlative ("le plus") + contexte transactionnel.

---

## 📋 Guide d'Utilisation pendant la Démo

### Préparation
1. Lancer le Data Agent depuis le workspace Fabric
2. S'assurer que le Lakehouse et le Semantic Model sont connectés
3. Tester 2-3 questions en amont pour valider la config

### Ordre Recommandé de Questions

**Phase 1 : Warm-up (2 min)**
- Questions 1, 2, 3 → montrer que ça fonctionne

**Phase 2 : Business value (5 min)**
- Questions 4, 5, 6 → calculs et insights commerce
- Questions 7, 8, 9, 10 → insights call center

**Phase 3 : Wow effect (5 min)**
- Questions 11, 12, 13 → jointures cross-domain
- Questions 14, 15 → insights avancés

**Phase 4 : Q&A (variable)**
- Questions bonus adaptées aux questions du public

### Tips de Présentation

✅ **DO** :
- Dire la question à voix haute avant de la poser
- Laisser le Data Agent répondre en temps réel (pas de skip)
- Commenter la qualité de la réponse ("Voyez, il a compris que...")
- Montrer le graphique généré si pertinent

❌ **DON'T** :
- Ne pas reformuler 10 fois si la réponse est mauvaise (passer à la suivante)
- Ne pas promettre une précision absolue ("Preview" = itératif)
- Ne pas poser de questions ambiguës volontairement

---

## 🔧 Troubleshooting

| Problème | Solution |
|----------|----------|
| Le Data Agent ne répond pas | Vérifier que le Semantic Model est publié et que le Data Agent est bien configuré dessus |
| Réponse incorrecte | Reformuler avec des termes présents dans les noms de colonnes (ex: "segment" au lieu de "type de client") |
| Graphique non proposé | Demander explicitement : "Affiche-moi ça en graphique" |
| Lenteur (>10s) | Simplifier la question ou vérifier la performance du workspace |

---

## 📊 Résumé : Capacités Démontrées

| Question | Capacité Démontrée |
|----------|-------------------|
| 1-3 | Compréhension langage naturel, filtres temporels |
| 4-6 | Calculs, agrégations, jointures simples |
| 7-10 | Métriques métier, KPI call center |
| 11-13 | Jointures cross-domain, analyses complexes |
| 14-15 | Insights prédictifs, identification de risques |

**Toutes les questions ensemble** → Démo complète de la puissance du Fabric Data Agent pour démocratiser l'accès aux données.

---

*Voir `data_agent_examples.md` pour 20 exemples supplémentaires avec réponses détaillées.*
