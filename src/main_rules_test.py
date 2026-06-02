# src/main_rules_test.py

from src.repositories.incident_rule_repository import (
    get_incident_rules,
)

rules = get_incident_rules()

for rule in rules:
    print(rule)