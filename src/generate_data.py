"""
Générateur de données synthétiques pour démo Microsoft Fabric
Customer 360 + Call Center + Transcripts

Usage:
    python generate_data.py
"""

import os
import sys
import yaml
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker
from typing import Dict, List, Tuple

# Configuration globale
CONFIG_FILE = Path(__file__).parent / "config.yaml"


class DataGenerator:
    """Générateur de données synthétiques pour la démo Fabric."""
    
    def __init__(self, config_path: Path):
        """Initialise le générateur avec la configuration."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser Faker avec seed pour reproductibilité
        seed = self.config['seed']
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        
        self.fake = Faker('fr_FR')
        
        # Dates
        self.start_date = datetime.fromisoformat(self.config['date_range']['start'])
        self.end_date = datetime.fromisoformat(self.config['date_range']['end'])
        
        # Chemins de sortie
        self.base_path = Path(__file__).parent.parent
        self.commerce_path = self.base_path / self.config['paths']['commerce']
        self.callcenter_path = self.base_path / self.config['paths']['callcenter']
        self.transcripts_path = self.base_path / self.config['paths']['transcripts']
        
        # Créer les dossiers si nécessaire
        self.commerce_path.mkdir(parents=True, exist_ok=True)
        self.callcenter_path.mkdir(parents=True, exist_ok=True)
        self.transcripts_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✓ Configuration chargée (seed={seed})")
    
    def random_date(self, start: datetime, end: datetime) -> datetime:
        """Génère une date aléatoire entre start et end."""
        delta = end - start
        random_days = random.randint(0, delta.days)
        random_seconds = random.randint(0, 86400)
        return start + timedelta(days=random_days, seconds=random_seconds)
    
    def generate_customers(self) -> pd.DataFrame:
        """Génère la table customers."""
        print("\n📊 Génération des clients...")
        n = self.config['volumes']['customers']
        segments = self.config['business_params']['customer_segments']
        
        customers = []
        for i in range(n):
            # Déterminer le segment
            rand = random.random() * 100
            if rand < segments['premium']:
                segment = 'premium'
            elif rand < segments['premium'] + segments['regular']:
                segment = 'regular'
            else:
                segment = 'occasional'
            
            customer = {
                'customer_id': f'CUST_{i+1:06d}',
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self.fake.email(),
                'phone': self.fake.phone_number(),
                'address': self.fake.street_address(),
                'city': self.fake.city(),
                'postal_code': self.fake.postcode(),
                'country': 'France',
                'segment': segment,
                'registration_date': self.random_date(
                    self.start_date - timedelta(days=365*2),
                    self.start_date
                ).strftime(self.config['output']['date_format']),
                'loyalty_points': random.randint(0, 5000) if segment != 'occasional' else 0
            }
            customers.append(customer)
        
        df = pd.DataFrame(customers)
        print(f"  ✓ {len(df)} clients générés")
        return df
    
    def generate_products(self) -> pd.DataFrame:
        """Génère la table products."""
        print("\n📦 Génération des produits...")
        products = []
        product_id = 1
        
        for category in self.config['products']['categories']:
            for i in range(category['count']):
                price = random.uniform(category['price_range'][0], category['price_range'][1])
                product = {
                    'product_id': f'PROD_{product_id:05d}',
                    'product_name': f"{category['name']} {self.fake.word().capitalize()} {self.fake.bothify('##??').upper()}",
                    'category': category['name'],
                    'price': round(price, 2),
                    'stock_quantity': random.randint(0, 500),
                    'supplier': self.fake.company(),
                    'failure_rate': category['failure_rate']
                }
                products.append(product)
                product_id += 1
        
        df = pd.DataFrame(products)
        print(f"  ✓ {len(df)} produits générés")
        return df
    
    def generate_orders(self, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Génère la table orders."""
        print("\n🛒 Génération des commandes...")
        n = self.config['volumes']['orders']
        orders = []
        
        # Calculer le nombre de commandes par client en fonction du segment
        premium_mult = self.config['business_params']['orders']['premium_order_multiplier']
        customer_weights = customers_df['segment'].map({
            'premium': premium_mult,
            'regular': 1.0,
            'occasional': 0.5
        }).values
        customer_weights = customer_weights / customer_weights.sum()
        
        for i in range(n):
            # Sélectionner un client avec pondération
            customer = customers_df.sample(n=1, weights=customer_weights).iloc[0]
            
            order_date = self.random_date(self.start_date, self.end_date)
            
            # Statut de la commande
            statuses = ['delivered', 'in_transit', 'processing', 'cancelled']
            status_weights = [0.75, 0.15, 0.08, 0.02]
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Dates de livraison
            if status == 'delivered':
                delivery_date = order_date + timedelta(days=random.randint(2, 10))
            elif status == 'in_transit':
                delivery_date = order_date + timedelta(days=random.randint(5, 15))
            else:
                delivery_date = None
            
            order = {
                'order_id': f'ORD_{i+1:07d}',
                'customer_id': customer['customer_id'],
                'order_date': order_date.strftime(self.config['output']['date_format']),
                'status': status,
                'delivery_date': delivery_date.strftime(self.config['output']['date_format']) if delivery_date else '',
                'shipping_address': f"{customer['address']}, {customer['postal_code']} {customer['city']}",
                'payment_method': random.choice(['card', 'paypal', 'bank_transfer']),
                'shipping_cost': round(random.uniform(5, 15), 2)
            }
            orders.append(order)
        
        df = pd.DataFrame(orders)
        print(f"  ✓ {len(df)} commandes générées")
        return df
    
    def generate_order_lines(self, orders_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
        """Génère la table order_lines."""
        print("\n📋 Génération des lignes de commande...")
        order_lines = []
        line_id = 1
        
        avg_lines = self.config['business_params']['orders']['avg_lines_per_order']
        max_lines = self.config['business_params']['orders']['max_lines_per_order']
        
        for _, order in orders_df.iterrows():
            # Nombre de lignes pour cette commande
            n_lines = min(int(np.random.poisson(avg_lines) + 1), max_lines)
            
            # Sélectionner des produits
            selected_products = products_df.sample(n=n_lines)
            
            for product in selected_products.itertuples():
                quantity = random.randint(1, 5)
                unit_price = product.price
                discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20])
                
                line = {
                    'line_id': f'LINE_{line_id:08d}',
                    'order_id': order['order_id'],
                    'product_id': product.product_id,
                    'quantity': quantity,
                    'unit_price': round(unit_price, 2),
                    'discount': discount,
                    'total_price': round(quantity * unit_price * (1 - discount), 2)
                }
                order_lines.append(line)
                line_id += 1
        
        df = pd.DataFrame(order_lines)
        print(f"  ✓ {len(df)} lignes de commande générées")
        return df
    
    def generate_agents(self) -> pd.DataFrame:
        """Génère la table agents."""
        print("\n👤 Génération des agents du call center...")
        n = self.config['volumes']['agents']
        exp_dist = self.config['agents']['experience_distribution']
        
        agents = []
        for i in range(n):
            # Déterminer le niveau d'expérience
            rand = random.random()
            if rand < exp_dist['junior']:
                experience = 'junior'
                years = random.randint(0, 2)
            elif rand < exp_dist['junior'] + exp_dist['senior']:
                experience = 'senior'
                years = random.randint(3, 7)
            else:
                experience = 'expert'
                years = random.randint(8, 15)
            
            agent = {
                'agent_id': f'AGENT_{i+1:03d}',
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self.fake.email(),
                'hire_date': self.random_date(
                    self.start_date - timedelta(days=365*years),
                    self.start_date
                ).strftime(self.config['output']['date_format']),
                'experience_level': experience,
                'languages': ','.join(random.sample(self.config['agents']['languages'], 
                                                   k=random.randint(1, 2)))
            }
            agents.append(agent)
        
        df = pd.DataFrame(agents)
        print(f"  ✓ {len(df)} agents générés")
        return df
    
    def generate_calls(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame, 
                      agents_df: pd.DataFrame, products_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """Génère la table calls et les métadonnées pour les transcripts."""
        print("\n📞 Génération des appels...")
        n = self.config['volumes']['calls']
        calls = []
        transcript_metadata = []
        
        reasons_config = self.config['business_params']['calls']['reasons']
        channels_config = self.config['business_params']['calls']['channels']
        
        # Préparer les listes de raisons et canaux avec leurs poids
        reasons = list(reasons_config.keys())
        reason_weights = list(reasons_config.values())
        channels = list(channels_config.keys())
        channel_weights = list(channels_config.values())
        
        for i in range(n):
            call_id = f'CALL_{i+1:06d}'
            
            # Sélectionner un client
            customer = customers_df.sample(n=1).iloc[0]
            
            # Date de l'appel
            call_date = self.random_date(self.start_date, self.end_date)
            
            # Raison et canal
            reason = random.choices(reasons, weights=reason_weights)[0]
            channel = random.choices(channels, weights=channel_weights)[0]
            
            # Agent
            agent = agents_df.sample(n=1).iloc[0]
            
            # Durée (en secondes)
            duration = int(np.random.gamma(3, 100))
            
            # Satisfaction (1-5)
            satisfaction_avg = self.config['business_params']['calls']['satisfaction']['avg']
            satisfaction_std = self.config['business_params']['calls']['satisfaction']['std_dev']
            satisfaction = int(np.clip(np.random.normal(satisfaction_avg, satisfaction_std), 1, 5))
            
            # Résolution
            resolution_rate = self.config['business_params']['calls']['resolution_rate']
            resolved = random.random() < resolution_rate
            
            # Déterminer le sentiment basé sur la satisfaction
            if satisfaction >= 4:
                sentiment = 'positive'
            elif satisfaction == 3:
                sentiment = 'neutral'
            else:
                sentiment = 'negative'
            
            # Trouver une commande associée (si pertinent)
            order_id = ''
            product_id = ''
            
            if reason in ['retard_livraison', 'remboursement', 'panne_produit']:
                # Chercher une commande récente du client
                customer_orders = orders_df[orders_df['customer_id'] == customer['customer_id']]
                if len(customer_orders) > 0:
                    # Filtrer par date (fenêtre temporelle)
                    window_days = self.config['business_params']['calls']['call_window_days']
                    customer_orders['order_datetime'] = pd.to_datetime(customer_orders['order_date'])
                    recent_orders = customer_orders[
                        (customer_orders['order_datetime'] >= call_date - timedelta(days=window_days)) &
                        (customer_orders['order_datetime'] <= call_date)
                    ]
                    
                    if len(recent_orders) > 0:
                        order_id = recent_orders.sample(n=1).iloc[0]['order_id']
                        # Sélectionner un produit aléatoire
                        product_id = products_df.sample(n=1).iloc[0]['product_id']
            
            call = {
                'call_id': call_id,
                'customer_id': customer['customer_id'],
                'agent_id': agent['agent_id'],
                'call_date': call_date.strftime(self.config['output']['date_format']),
                'channel': channel,
                'reason': reason,
                'duration_seconds': duration,
                'satisfaction': satisfaction,
                'resolved': 1 if resolved else 0,
                'order_id': order_id,
                'product_id': product_id
            }
            calls.append(call)
            
            # Métadonnées pour le transcript
            transcript_metadata.append({
                'call_id': call_id,
                'customer_id': customer['customer_id'],
                'customer_name': f"{customer['first_name']} {customer['last_name']}",
                'call_date': call_date,
                'reason': reason,
                'product_id': product_id,
                'order_id': order_id,
                'sentiment': sentiment,
                'satisfaction': satisfaction,
                'resolved': resolved,
                'agent_name': f"{agent['first_name']} {agent['last_name']}"
            })
        
        df = pd.DataFrame(calls)
        print(f"  ✓ {len(df)} appels générés")
        return df, transcript_metadata
    
    def generate_transcript_text(self, metadata: Dict) -> str:
        """Génère le contenu textuel d'un transcript."""
        lines = []
        
        # En-tête
        lines.append(f"CALL_ID: {metadata['call_id']}")
        lines.append(f"CUSTOMER_ID: {metadata['customer_id']}")
        lines.append(f"DATE: {metadata['call_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"PRODUCT: {metadata['product_id']}")
        lines.append(f"REASON: {metadata['reason']}")
        lines.append("")
        lines.append("=== TRANSCRIPT ===")
        lines.append("")
        
        # Nombre d'échanges
        avg_exchanges = self.config['business_params']['transcripts']['avg_exchanges']
        std_exchanges = self.config['business_params']['transcripts']['std_dev_exchanges']
        n_exchanges = max(3, int(np.random.normal(avg_exchanges, std_exchanges)))
        
        # Templates de dialogue par raison
        templates = self._get_dialogue_templates(metadata['reason'], metadata['sentiment'])
        
        # Générer les échanges
        for i in range(n_exchanges):
            if i == 0:
                # Ouverture
                lines.append(f"Agent: Bonjour, {metadata['agent_name']} à votre service. Comment puis-je vous aider ?")
                lines.append(f"Client: {random.choice(templates['opening'])}")
            elif i == n_exchanges - 1:
                # Clôture
                if metadata['resolved']:
                    lines.append(f"Agent: {random.choice(templates['closing_positive'])}")
                    lines.append(f"Client: {random.choice(['Merci beaucoup !', 'Parfait, merci.', 'Super, bonne journée !'])}")
                else:
                    lines.append(f"Agent: {random.choice(templates['closing_negative'])}")
                    lines.append(f"Client: {random.choice(['Bon, je vais voir...', 'Pas très satisfait mais bon.', 'Dommage.'])}")
            else:
                # Milieu de conversation
                lines.append(f"Agent: {random.choice(templates['middle_agent'])}")
                lines.append(f"Client: {random.choice(templates['middle_client'])}")
        
        # Ajouter de fausses PII si configuré
        if self.config['business_params']['transcripts']['include_fake_pii']:
            if random.random() < self.config['business_params']['transcripts']['pii_probability']:
                lines.append("")
                lines.append(f"Client: Mon email est {self.fake.email()} au cas où.")
                lines.append(f"Agent: Noté, merci.")
        
        return "\n".join(lines)
    
    def _get_dialogue_templates(self, reason: str, sentiment: str) -> Dict[str, List[str]]:
        """Retourne des templates de dialogue selon la raison et le sentiment."""
        templates = {
            'retard_livraison': {
                'opening': [
                    "Bonjour, j'ai commandé il y a une semaine et je n'ai toujours rien reçu.",
                    "Ma commande devait arriver hier mais rien...",
                    "Je voudrais savoir où en est ma livraison, c'est très long."
                ],
                'middle_agent': [
                    "Je vérifie cela pour vous. Pouvez-vous me donner votre numéro de commande ?",
                    "Je comprends votre frustration. Laissez-moi consulter le statut.",
                    "Un instant s'il vous plaît, je regarde où se trouve votre colis."
                ],
                'middle_client': [
                    "C'est marqué 'en transit' depuis 5 jours.",
                    "Je ne comprends pas le retard.",
                    "J'en ai vraiment besoin rapidement."
                ],
                'closing_positive': [
                    "Votre colis sera livré demain au plus tard. Je vous envoie un email de confirmation.",
                    "Tout est en ordre, vous recevrez votre commande sous 48h.",
                    "Je m'excuse pour le retard. Livraison garantie demain matin."
                ],
                'closing_negative': [
                    "Le colis est bloqué en entrepôt. Nous faisons le maximum.",
                    "Malheureusement, il y a un délai supplémentaire de 3 jours.",
                    "Je ne peux pas accélérer la livraison, désolé."
                ]
            },
            'remboursement': {
                'opening': [
                    "Je voudrais me faire rembourser ma dernière commande.",
                    "Le produit ne me convient pas, je veux un remboursement.",
                    "Comment faire pour annuler ma commande et être remboursé ?"
                ],
                'middle_agent': [
                    "Quel est le motif de votre demande de remboursement ?",
                    "Je peux initier la procédure. Avez-vous retourné le produit ?",
                    "Pas de problème, je vais traiter cela pour vous."
                ],
                'middle_client': [
                    "Le produit est défectueux.",
                    "Je n'en ai plus l'utilité.",
                    "Ce n'est pas ce que j'attendais."
                ],
                'closing_positive': [
                    "Remboursement validé, vous serez crédité sous 5 jours ouvrés.",
                    "Tout est en ordre, le remboursement est en cours.",
                    "Pas de souci, vous recevrez votre argent dans les 7 jours."
                ],
                'closing_negative': [
                    "Malheureusement le délai de rétractation est dépassé.",
                    "Je ne peux pas valider ce remboursement sans retour du produit.",
                    "Selon nos conditions, ce cas n'est pas éligible au remboursement."
                ]
            },
            'panne_produit': {
                'opening': [
                    "Mon appareil ne fonctionne plus depuis hier.",
                    "Le produit que j'ai reçu est en panne.",
                    "J'ai un problème avec mon achat, ça ne marche pas."
                ],
                'middle_agent': [
                    "Pouvez-vous me décrire le problème exactement ?",
                    "Est-ce que l'appareil s'allume au moins ?",
                    "Je vais vous guider pour diagnostiquer le problème."
                ],
                'middle_client': [
                    "Ça ne s'allume plus du tout.",
                    "Il y a un message d'erreur bizarre.",
                    "J'ai tout essayé, rien ne fonctionne."
                ],
                'closing_positive': [
                    "Je vous envoie un produit de remplacement dès aujourd'hui.",
                    "Nous allons procéder à un échange sous garantie.",
                    "Pas de problème, un nouveau produit vous sera expédié."
                ],
                'closing_negative': [
                    "Le produit n'est plus sous garantie malheureusement.",
                    "Il faudra l'envoyer en réparation, comptez 2 semaines.",
                    "Ce type de panne n'est pas couvert par la garantie."
                ]
            }
        }
        
        # Template générique pour les autres raisons
        generic = {
            'opening': [
                "Bonjour, j'ai une question sur un produit.",
                "Je voudrais des informations s'il vous plaît.",
                "J'ai besoin d'aide pour comprendre quelque chose."
            ],
            'middle_agent': [
                "Je peux certainement vous aider avec ça.",
                "Quelle est votre question exactement ?",
                "Je vous écoute."
            ],
            'middle_client': [
                "Voilà, je me demandais...",
                "En fait, c'est à propos de...",
                "D'accord, je comprends mieux."
            ],
            'closing_positive': [
                "Parfait, je pense avoir répondu à vos questions.",
                "Tout est clair maintenant ? Parfait !",
                "Ravi d'avoir pu vous aider."
            ],
            'closing_negative': [
                "Je vais escalader votre demande à mon superviseur.",
                "Je n'ai pas la réponse, je vous recontacte.",
                "C'est noté, nous allons étudier ça."
            ]
        }
        
        # Ajuster le sentiment
        result = templates.get(reason, generic).copy()
        
        if sentiment == 'negative':
            result['middle_client'] = [
                "C'est vraiment pas normal.",
                "Je suis très déçu de votre service.",
                "C'est inadmissible."
            ]
        elif sentiment == 'positive':
            result['middle_client'] = [
                "D'accord, merci pour votre aide.",
                "Je comprends, pas de problème.",
                "Super, merci beaucoup."
            ]
        
        return result
    
    def generate_transcripts(self, transcript_metadata: List[Dict]) -> None:
        """Génère les fichiers de transcripts (.txt)."""
        print("\n💬 Génération des transcripts...")
        
        for i, metadata in enumerate(transcript_metadata):
            transcript_text = self.generate_transcript_text(metadata)
            
            # Nom du fichier
            filename = f"{metadata['call_id']}.txt"
            filepath = self.transcripts_path / filename
            
            # Écrire le fichier
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            
            if (i + 1) % 500 == 0:
                print(f"  ✓ {i + 1}/{len(transcript_metadata)} transcripts générés")
        
        print(f"  ✓ {len(transcript_metadata)} transcripts générés")
    
    def save_csv(self, df: pd.DataFrame, filename: str, path: Path) -> None:
        """Sauvegarde un DataFrame en CSV."""
        filepath = path / filename
        df.to_csv(filepath, index=False, encoding=self.config['output']['encoding'],
                 sep=self.config['output']['csv_separator'])
        print(f"  → {filename} sauvegardé ({len(df)} lignes)")
    
    def generate_all(self) -> None:
        """Génère toutes les données."""
        print("\n" + "="*60)
        print("🚀 GÉNÉRATION DES DONNÉES SYNTHÉTIQUES")
        print("="*60)
        
        # 1. Customers
        customers_df = self.generate_customers()
        self.save_csv(customers_df, 'customers.csv', self.commerce_path)
        
        # 2. Products
        products_df = self.generate_products()
        self.save_csv(products_df, 'products.csv', self.commerce_path)
        
        # 3. Orders
        orders_df = self.generate_orders(customers_df)
        self.save_csv(orders_df, 'orders.csv', self.commerce_path)
        
        # 4. Order Lines
        order_lines_df = self.generate_order_lines(orders_df, products_df)
        self.save_csv(order_lines_df, 'order_lines.csv', self.commerce_path)
        
        # 5. Agents
        agents_df = self.generate_agents()
        self.save_csv(agents_df, 'agents.csv', self.callcenter_path)
        
        # 6. Calls + transcript metadata
        calls_df, transcript_metadata = self.generate_calls(
            customers_df, orders_df, agents_df, products_df
        )
        self.save_csv(calls_df, 'calls.csv', self.callcenter_path)
        
        # 7. Transcripts
        self.generate_transcripts(transcript_metadata)
        
        print("\n" + "="*60)
        print("✅ GÉNÉRATION TERMINÉE")
        print("="*60)
        print(f"\n📁 Fichiers générés dans :")
        print(f"  - {self.commerce_path}")
        print(f"  - {self.callcenter_path}")
        print(f"  - {self.transcripts_path}")
        print(f"\n📊 Statistiques :")
        print(f"  - Clients: {len(customers_df)}")
        print(f"  - Produits: {len(products_df)}")
        print(f"  - Commandes: {len(orders_df)}")
        print(f"  - Lignes de commande: {len(order_lines_df)}")
        print(f"  - Agents: {len(agents_df)}")
        print(f"  - Appels: {len(calls_df)}")
        print(f"  - Transcripts: {len(transcript_metadata)}")
        print()


def main():
    """Point d'entrée principal."""
    try:
        generator = DataGenerator(CONFIG_FILE)
        generator.generate_all()
        return 0
    except Exception as e:
        print(f"\n❌ ERREUR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
