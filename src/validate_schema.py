"""
Script de Validation des Noms de Colonnes - Call Center Demo

Vérifie que tous les noms de colonnes correspondent au schéma attendu
et que les données sont cohérentes pour les DAX queries.

Usage:
    cd src
    python validate_schema.py
"""

import pandas as pd
import sys
from pathlib import Path

class SchemaValidator:
    def __init__(self, data_root='../data/raw'):
        self.data_root = Path(data_root)
        self.errors = []
        self.warnings = []
        
    def validate_all(self):
        """Exécute toutes les validations"""
        print("=" * 80)
        print("VALIDATION DES SCHEMAS - Call Center Demo")
        print("=" * 80)
        print()
        
        # Validation des tables Commerce
        self.validate_commerce_tables()
        
        # Validation des tables Call Center
        self.validate_callcenter_tables()
        
        # Validation des relations
        self.validate_relationships()
        
        # Afficher le résumé
        self.print_summary()
        
        return len(self.errors) == 0
    
    def validate_commerce_tables(self):
        """Valide les tables Commerce"""
        print("--- Validation Commerce Tables ---")
        
        # customers
        customers = self.load_csv('commerce/dim_customers.csv')
        if customers is not None:
            self.check_columns(customers, 'dim_customers', [
                'customer_id', 'email', 'registration_date', 'segment',
                'country', 'preferred_language'
            ])
            
            # Vérifier format customer_id
            sample_id = customers['customer_id'].iloc[0]
            if not sample_id.startswith('CUST_'):
                self.errors.append("customers.customer_id doit être au format 'CUST_XXXXXX'")
        
        # products
        products = self.load_csv('commerce/dim_products.csv')
        if products is not None:
            self.check_columns(products, 'dim_products', [
                'product_id', 'product_name', 'category', 'price_eur'
            ])
        
        # orders
        orders = self.load_csv('commerce/fact_orders.csv')
        if orders is not None:
            self.check_columns(orders, 'fact_orders', [
                'order_id', 'customer_id', 'order_at', 'total_amount_eur', 'status'
            ])
        
        # order_lines
        lines = self.load_csv('commerce/fact_order_lines.csv')
        if lines is not None:
            self.check_columns(lines, 'fact_order_lines', [
                'order_line_id', 'order_id', 'product_id', 'qty',
                'unit_price_eur', 'line_total_eur'
            ])
        
        print()
    
    def validate_callcenter_tables(self):
        """Valide les tables Call Center"""
        print("--- Validation Call Center Tables ---")
        
        # calls (CRITIQUE pour DAX)
        calls = self.load_csv('callcenter/fact_calls.csv')
        if calls is not None:
            self.check_columns(calls, 'fact_calls', [
                'call_id', 'customer_id', 'agent_id', 'call_start',
                'call_duration', 'reason', 'satisfaction_score', 'resolved'
            ])
            
            # Vérifier call_id format
            sample_id = calls['call_id'].iloc[0]
            if not sample_id.startswith('CALL_'):
                self.errors.append("calls.call_id doit être au format 'CALL_XXXXXX'")
            
            # Vérifier satisfaction_score (CRITIQUE)
            if 'satisfaction_score' in calls.columns:
                min_score = calls['satisfaction_score'].min()
                max_score = calls['satisfaction_score'].max()
                
                if min_score < 1 or max_score > 5:
                    self.errors.append(
                        f"calls.satisfaction_score doit être entre 1 et 5. "
                        f"Trouvé: min={min_score}, max={max_score}"
                    )
                else:
                    print(f"  ✅ calls.satisfaction_score correct (1-5)")
            
            # Vérifier reason values
            if 'reason' in calls.columns:
                reasons = calls['reason'].unique()
                print(f"  ℹ️  Raisons d'appel: {len(reasons)} types trouvés")
        
        # agents
        agents = self.load_csv('callcenter/dim_agents.csv')
        if agents is not None:
            self.check_columns(agents, 'dim_agents', [
                'agent_id', 'agent_name', 'hire_date', 'specialization'
            ])
        
        print()
    
    def validate_relationships(self):
        """Valide les relations entre tables (foreign keys)"""
        print("--- Validation Relations (Foreign Keys) ---")
        
        # Charger les tables principales
        customers = self.load_csv('commerce/dim_customers.csv')
        calls = self.load_csv('callcenter/fact_calls.csv')
        agents = self.load_csv('callcenter/dim_agents.csv')
        orders = self.load_csv('commerce/fact_orders.csv')
        
        if customers is None or calls is None or agents is None:
            self.errors.append("Impossible de valider les relations: tables manquantes")
            return
        
        # Vérifier calls.customer_id → customers.customer_id
        invalid_customers = ~calls['customer_id'].isin(customers['customer_id'])
        if invalid_customers.any():
            self.errors.append(
                f"{invalid_customers.sum()} calls avec customer_id invalide"
            )
        else:
            print(f"  ✅ calls.customer_id → customers.customer_id (100% valide)")
        
        # Vérifier calls.agent_id → agents.agent_id
        invalid_agents = ~calls['agent_id'].isin(agents['agent_id'])
        if invalid_agents.any():
            self.errors.append(
                f"{invalid_agents.sum()} calls avec agent_id invalide"
            )
        else:
            print(f"  ✅ calls.agent_id → agents.agent_id (100% valide)")
        
        # Vérifier orders.customer_id → customers.customer_id
        if orders is not None:
            invalid_order_customers = ~orders['customer_id'].isin(customers['customer_id'])
            if invalid_order_customers.any():
                self.errors.append(
                    f"{invalid_order_customers.sum()} orders avec customer_id invalide"
                )
            else:
                print(f"  ✅ orders.customer_id → customers.customer_id (100% valide)")
        
        print()
    
    def check_columns(self, df, table_name, expected_columns):
        """Vérifie que les colonnes attendues sont présentes"""
        missing = set(expected_columns) - set(df.columns)
        extra = set(df.columns) - set(expected_columns)
        
        if missing:
            self.errors.append(f"{table_name}: colonnes manquantes: {missing}")
        
        if extra:
            self.warnings.append(f"{table_name}: colonnes inattendues: {extra}")
        
        if not missing and not extra:
            print(f"  ✅ {table_name}: {len(expected_columns)} colonnes valides")
    
    def load_csv(self, relative_path):
        """Charge un CSV et gère les erreurs"""
        filepath = self.data_root / relative_path
        
        if not filepath.exists():
            self.errors.append(f"Fichier manquant: {filepath}")
            return None
        
        try:
            return pd.read_csv(filepath, encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Erreur lecture {filepath}: {e}")
            return None
    
    def print_summary(self):
        """Affiche le résumé des validations"""
        print("=" * 80)
        print("RÉSUMÉ DE VALIDATION")
        print("=" * 80)
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} AVERTISSEMENT(S):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print(f"\n❌ {len(self.errors)} ERREUR(S):")
            for error in self.errors:
                print(f"  - {error}")
            print("\n🔧 ACTIONS REQUISES:")
            print("  1. Corriger les erreurs listées ci-dessus")
            print("  2. Régénérer les données avec generate_data.py")
            print("  3. Relancer ce script de validation")
            print("\n❌ VALIDATION ÉCHOUÉE")
        else:
            print("\n✅ VALIDATION RÉUSSIE - Tous les schémas sont corrects !")
            print("\n✅ Les DAX queries devraient fonctionner correctement.")
        
        print("=" * 80)


def main():
    """Point d'entrée principal"""
    validator = SchemaValidator()
    success = validator.validate_all()
    
    # Exit code pour CI/CD
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
