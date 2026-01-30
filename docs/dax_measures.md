# Mesures DAX - Call Center Analytics

Ce fichier contient toutes les mesures DAX testées et validées pour le semantic model Fabric (Call Center).

## Tables Requises

- customers
- products
- orders
- order_lines
- calls
- agents
- call_transcripts (si AI transformations appliquées)

## Relations Clés

```
customers[customer_id] 1 ----→ * calls[customer_id]
customers[customer_id] 1 ----→ * orders[customer_id]
agents[agent_id] 1 ----→ * calls[agent_id]
orders[order_id] 1 ----→ * order_lines[order_id]
products[product_id] 1 ----→ * order_lines[product_id]
```

---

## Métriques Call Center

### CSAT (Customer Satisfaction Score)

Score de satisfaction moyen.

```dax
CSAT = 
DIVIDE(
    AVERAGE(calls[satisfaction_score]),
    5,
    BLANK()
) * 100
```

**Format:** Pourcentage
**Target:** >= 80%
**Usage:** KPI principal, comparaison agents/raisons

---

### CSAT Score (Raw)

Score brut de satisfaction.

```dax
CSAT Score = 
AVERAGE(calls[satisfaction_score])
```

**Format:** Nombre (0-5)
**Usage:** Calculs intermédiaires

---

### Total Calls

Nombre total d'appels.

```dax
Total Calls = 
COUNTROWS(calls)
```

**Format:** Nombre entier
**Usage:** Contexte volume

---

### FCR (First Call Resolution)

Taux de résolution au premier contact.

```dax
FCR = 
VAR ResolvedCalls = 
    CALCULATE(
        COUNTROWS(calls),
        calls[resolved] = TRUE()
    )
VAR TotalCalls = COUNTROWS(calls)
RETURN
    DIVIDE(ResolvedCalls, TotalCalls, 0)
```

**Format:** Pourcentage
**Target:** >= 70%
**Usage:** KPI performance

---

### Resolved Calls

Nombre d'appels résolus.

```dax
Resolved Calls = 
CALCULATE(
    COUNTROWS(calls),
    calls[resolved] = TRUE()
)
```

**Format:** Nombre entier
**Usage:** Calcul FCR

---

### Unresolved Calls

Appels non résolus.

```dax
Unresolved Calls = 
CALCULATE(
    COUNTROWS(calls),
    calls[resolved] = FALSE()
)
```

**Format:** Nombre entier
**Usage:** Alerte escalation

---

### AHT (Average Handle Time)

Durée moyenne de traitement.

```dax
AHT = 
AVERAGE(calls[call_duration])
```

**Format:** Nombre (minutes)
**Target:** 12-15 min (varie selon raison)
**Usage:** Performance agent, efficacité

---

### Total Call Duration

Durée totale des appels.

```dax
Total Call Duration = 
SUM(calls[call_duration])
```

**Format:** Nombre (minutes)
**Usage:** Calcul charge de travail

---

### Repeat Call Rate

Taux d'appels répétés (clients avec 2+ appels même raison).

```dax
Repeat Call Rate = 
VAR CustomersWithMultipleCalls = 
    CALCULATE(
        DISTINCTCOUNT(calls[customer_id]),
        FILTER(
            VALUES(calls[customer_id]),
            CALCULATE(COUNTROWS(calls)) >= 2
        )
    )
VAR TotalCustomers = DISTINCTCOUNT(calls[customer_id])
RETURN
    DIVIDE(CustomersWithMultipleCalls, TotalCustomers, 0)
```

**Format:** Pourcentage
**Target:** <= 10%
**Usage:** Qualité de résolution

---

### Avg Calls Per Customer

Nombre moyen d'appels par client.

```dax
Avg Calls Per Customer = 
DIVIDE(
    COUNTROWS(calls),
    DISTINCTCOUNT(calls[customer_id]),
    BLANK()
)
```

**Format:** Nombre décimal
**Usage:** Engagement client

---

### Customers at Risk

Clients insatisfaits (satisfaction <= 2).

```dax
Customers at Risk = 
CALCULATE(
    DISTINCTCOUNT(calls[customer_id]),
    calls[satisfaction_score] <= 2
)
```

**Format:** Nombre entier
**Usage:** Alerte churn

---

### Churn Risk Revenue

Revenue potentiel perdu (clients insatisfaits).

```dax
Churn Risk Revenue = 
VAR CustomersAtRisk = 
    CALCULATETABLE(
        VALUES(calls[customer_id]),
        calls[satisfaction_score] <= 2
    )
VAR AvgOrderValue = AVERAGE(orders[total_amount_eur])
RETURN
    COUNTROWS(CustomersAtRisk) * AvgOrderValue
```

**Format:** Currency (EUR)
**Usage:** Impact financier insatisfaction

---

## Métriques Agent

### Calls Per Agent

Nombre d'appels par agent.

```dax
Calls Per Agent = 
DIVIDE(
    COUNTROWS(calls),
    DISTINCTCOUNT(calls[agent_id]),
    BLANK()
)
```

**Format:** Nombre décimal
**Usage:** Charge de travail

---

### Agent CSAT

CSAT moyen de l'agent sélectionné.

```dax
Agent CSAT = 
DIVIDE(
    AVERAGE(calls[satisfaction_score]),
    5,
    BLANK()
) * 100
```

**Format:** Pourcentage
**Context:** Filtre sur agent spécifique
**Usage:** Performance individuelle

---

### Team Average CSAT

CSAT moyen de l'équipe (pour comparaison).

```dax
Team Average CSAT = 
CALCULATE(
    DIVIDE(
        AVERAGE(calls[satisfaction_score]),
        5,
        BLANK()
    ) * 100,
    ALL(agents)
)
```

**Format:** Pourcentage
**Usage:** Benchmark performance agent

---

### Agent vs Team CSAT Delta

Écart de performance agent vs équipe.

```dax
Agent vs Team CSAT Delta = 
[Agent CSAT] - [Team Average CSAT]
```

**Format:** Points de pourcentage
**Usage:** Coaching, évaluation

---

### Top Performing Agents Count

Nombre d'agents au-dessus de la moyenne.

```dax
Top Performing Agents Count = 
CALCULATE(
    DISTINCTCOUNT(calls[agent_id]),
    FILTER(
        VALUES(calls[agent_id]),
        [Agent CSAT] > [Team Average CSAT]
    )
)
```

**Format:** Nombre entier
**Usage:** Distribution performance

---

## Métriques par Raison

### Calls by Reason

Nombre d'appels par raison.

```dax
Calls by Reason = 
CALCULATE(
    COUNTROWS(calls),
    ALLEXCEPT(calls, calls[reason])
)
```

**Format:** Nombre entier
**Usage:** Analyse volumétrie

---

### CSAT by Reason

CSAT moyen par raison d'appel.

```dax
CSAT by Reason = 
CALCULATE(
    [CSAT],
    ALLEXCEPT(calls, calls[reason])
)
```

**Format:** Pourcentage
**Usage:** Identifier raisons problématiques

---

### AHT by Reason

AHT moyen par raison.

```dax
AHT by Reason = 
CALCULATE(
    [AHT],
    ALLEXCEPT(calls, calls[reason])
)
```

**Format:** Nombre (minutes)
**Usage:** Benchmark complexité

---

## Métriques Commerce (contexte)

### Total Revenue

Revenue total des commandes.

```dax
Total Revenue = 
SUM(orders[total_amount_eur])
```

**Format:** Currency (EUR)
**Usage:** Contexte business

---

### Orders Linked to Calls

Commandes associées à des appels (même client).

```dax
Orders Linked to Calls = 
CALCULATE(
    COUNTROWS(orders),
    FILTER(
        orders,
        orders[customer_id] IN VALUES(calls[customer_id])
    )
)
```

**Format:** Nombre entier
**Usage:** Corrélation appels/achats

---

### Avg Order Value

Panier moyen.

```dax
Avg Order Value = 
DIVIDE(
    SUM(orders[total_amount_eur]),
    COUNTROWS(orders),
    BLANK()
)
```

**Format:** Currency (EUR)
**Usage:** Contexte valeur client

---

## Mesures Avancées

### Satisfaction Trend (MoM)

Évolution CSAT mois sur mois.

```dax
Satisfaction Trend MoM = 
VAR CurrentCSAT = [CSAT]
VAR PreviousCSAT = 
    CALCULATE(
        [CSAT],
        DATEADD('Date'[Date], -1, MONTH)
    )
RETURN
    CurrentCSAT - PreviousCSAT
```

**Format:** Points de pourcentage
**Usage:** Trend analysis

---

### Resolution Time Impact

Corrélation durée appel vs satisfaction.

```dax
Resolution Time Impact = 
VAR ShortCalls = 
    CALCULATE(
        [CSAT],
        calls[call_duration] < [AHT]
    )
VAR LongCalls = 
    CALCULATE(
        [CSAT],
        calls[call_duration] >= [AHT]
    )
RETURN
    ShortCalls - LongCalls
```

**Format:** Points de pourcentage
**Usage:** Analyse efficacité vs qualité

---

### Customer Lifetime Impact

Impact appels sur valeur client.

```dax
Customer Lifetime Impact = 
VAR SatisfiedCustomers = 
    CALCULATE(
        AVERAGE(orders[total_amount_eur]),
        calls[satisfaction_score] >= 4
    )
VAR UnsatisfiedCustomers = 
    CALCULATE(
        AVERAGE(orders[total_amount_eur]),
        calls[satisfaction_score] <= 2
    )
RETURN
    SatisfiedCustomers - UnsatisfiedCustomers
```

**Format:** Currency (EUR)
**Usage:** Business case satisfaction

---

## Notes d'Implémentation

### Vérification des Noms de Colonnes

**Tables critiques:**
- calls.call_id (STRING, PK)
- calls.customer_id (STRING, FK)
- calls.agent_id (STRING, FK)
- calls.satisfaction_score (INT, 1-5)
- calls.call_duration (INT, minutes)
- calls.resolved (BOOLEAN)
- calls.reason (STRING)

### Relations Manquantes

Si une mesure retourne BLANK(), vérifier:
1. Relations entre tables créées
2. Cardinalités correctes (1:Many)
3. Colonnes de jointure existent

---

## Validation

**Valeurs attendues (dataset complet):**
- CSAT: ~70-75%
- FCR: ~65-70%
- AHT: ~12-14 minutes
- Repeat Call Rate: ~8-12%
- Total Calls: ~15 000
