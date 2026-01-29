"""
Comprehensive validator that checks:
- Intent accuracy
- Entity extraction (category, merchant, amount)
- Date parsing correctness
- Result validity
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional


class ComprehensiveValidator:
    """Validates all aspects of query processing"""
    
    def __init__(self, csv_path="data/transactions.csv"):
        self.df = pd.read_csv(csv_path)
        self.df["date"] = pd.to_datetime(self.df["date"])
        
        self.min_date = self.df["date"].min()
        self.max_date = self.df["date"].max()
        self.categories = set(self.df["category"].unique())
        self.merchants = set(self.df["merchant"].unique())
        
    def validate_query(
        self, 
        query: str,
        expected: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of a single query
        
        Returns:
            {
                "passed": bool,
                "intent_match": bool,
                "entity_match": bool,
                "date_match": bool,
                "result_valid": bool,
                "issues": List[str],
                "warnings": List[str]
            }
        """
        issues = []
        warnings = []
        
        # 1. INTENT VALIDATION
        intent_match = self._validate_intent(expected, actual, issues)
        
        # 2. ENTITY VALIDATION
        entity_match = self._validate_entities(expected, actual, issues, warnings)
        
        # 3. DATE VALIDATION
        date_match = self._validate_dates(expected, actual, issues, warnings)
        
        # 4. RESULT VALIDATION
        result_valid = self._validate_result(
            expected, actual, query, issues, warnings
        )
        
        passed = (intent_match and entity_match and date_match and result_valid)
        
        return {
            "passed": passed,
            "intent_match": intent_match,
            "entity_match": entity_match,
            "date_match": date_match,
            "result_valid": result_valid,
            "issues": issues,
            "warnings": warnings
        }
    
    def _validate_intent(
        self, 
        expected: Dict, 
        actual: Dict, 
        issues: List[str]
    ) -> bool:
        """Validate intent detection"""
        expected_intent = expected.get("intent", {}).get("intent")
        actual_intent = actual.get("intent", {}).get("intent")
        
        if expected_intent != actual_intent:
            issues.append(
                f"❌ Intent mismatch: expected '{expected_intent}', "
                f"got '{actual_intent}'"
            )
            return False
        
        # Check confidence score
        score = actual.get("intent", {}).get("score", 0)
        if score < 0.5:
            issues.append(
                f"⚠️ Low confidence score: {score:.3f} (< 0.5)"
            )
        
        return True
    
    def _validate_entities(
        self, 
        expected: Dict, 
        actual: Dict, 
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate entity extraction"""
        expected_entities = expected.get("entities", {})
        actual_entities = actual.get("entities", {})
        
        match = True
        
        # Check category
        exp_cat = expected_entities.get("category")
        act_cat = actual_entities.get("category")
        
        if exp_cat != act_cat:
            issues.append(
                f"❌ Category mismatch: expected '{exp_cat}', got '{act_cat}'"
            )
            match = False
        
        # Validate category exists in dataset
        if act_cat and act_cat not in self.categories:
            warnings.append(
                f"⚠️ Category '{act_cat}' not in dataset. "
                f"Available: {sorted(self.categories)}"
            )
        
        # Check merchant
        exp_mer = expected_entities.get("merchant")
        act_mer = actual_entities.get("merchant")
        
        if exp_mer != act_mer:
            issues.append(
                f"❌ Merchant mismatch: expected '{exp_mer}', got '{act_mer}'"
            )
            match = False
        
        # Validate merchant exists in dataset
        if act_mer and act_mer not in self.merchants:
            warnings.append(
                f"⚠️ Merchant '{act_mer}' not in dataset. "
                f"Did you mean one of: {self._suggest_merchants(act_mer)}"
            )
        
        # Check amount threshold
        exp_amt = expected_entities.get("amount")
        act_amt = actual_entities.get("amount")
        
        if exp_amt != act_amt:
            issues.append(
                f"❌ Amount threshold mismatch: expected {exp_amt}, got {act_amt}"
            )
            match = False
        
        return match
    
    def _validate_dates(
        self, 
        expected: Dict, 
        actual: Dict, 
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate date parsing"""
        exp_start = expected.get("start_date")
        exp_end = expected.get("end_date")
        
        act_start = actual.get("start_date")
        act_end = actual.get("end_date")
        
        # Convert strings to datetime for comparison
        def parse_date(d):
            if d is None:
                return None
            if isinstance(d, str):
                return datetime.fromisoformat(d.replace('Z', '+00:00'))
            return d
        
        exp_start = parse_date(exp_start)
        exp_end = parse_date(exp_end)
        act_start = parse_date(act_start)
        act_end = parse_date(act_end)
        
        match = True
        
        # Compare start dates (allow same day)
        if exp_start and act_start:
            if exp_start.date() != act_start.date():
                issues.append(
                    f"❌ Start date mismatch: expected {exp_start.date()}, "
                    f"got {act_start.date()}"
                )
                match = False
        elif exp_start != act_start:  # One is None, other isn't
            issues.append(
                f"❌ Start date mismatch: expected {exp_start}, got {act_start}"
            )
            match = False
        
        # Compare end dates
        if exp_end and act_end:
            if exp_end.date() != act_end.date():
                issues.append(
                    f"❌ End date mismatch: expected {exp_end.date()}, "
                    f"got {act_end.date()}"
                )
                match = False
        elif exp_end != act_end:
            issues.append(
                f"❌ End date mismatch: expected {exp_end}, got {act_end}"
            )
            match = False
        
        # Check if dates are within dataset range
        if act_start and act_end:
            if act_start.date() > self.max_date.date():
                warnings.append(
                    f"⚠️ Query date range ({act_start.date()} to {act_end.date()}) "
                    f"is after dataset max date ({self.max_date.date()})"
                )
            if act_end.date() < self.min_date.date():
                warnings.append(
                    f"⚠️ Query date range is before dataset min date "
                    f"({self.min_date.date()})"
                )
        
        return match
    
    def _validate_result(
        self, 
        expected: Dict, 
        actual: Dict, 
        query: str,
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate result correctness"""
        exp_result = expected.get("result")
        act_result = actual.get("result")
        
        # Type check
        if type(exp_result) != type(act_result):
            issues.append(
                f"❌ Result type mismatch: expected {type(exp_result).__name__}, "
                f"got {type(act_result).__name__}"
            )
            return False
        
        # Validate based on type
        if isinstance(exp_result, (int, float)):
            return self._validate_numeric_result(
                exp_result, act_result, issues, warnings
            )
        elif isinstance(exp_result, list):
            return self._validate_list_result(
                exp_result, act_result, issues, warnings
            )
        elif isinstance(exp_result, dict):
            return self._validate_dict_result(
                exp_result, act_result, issues, warnings
            )
        elif isinstance(exp_result, str):
            return self._validate_string_result(
                exp_result, act_result, issues, warnings
            )
        
        return True
    
    def _validate_numeric_result(
        self, 
        expected: float, 
        actual: float, 
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate numeric results (total_spend, average_spend)"""
        # Allow small floating point differences
        tolerance = 0.01
        
        if abs(expected - actual) > tolerance:
            issues.append(
                f"❌ Numeric result mismatch: expected {expected}, got {actual}"
            )
            return False
        
        # Sanity checks
        if actual == 0:
            warnings.append("⚠️ Result is zero - may indicate over-filtering")
        
        if actual < 0:
            issues.append(f"❌ Negative result: {actual}")
            return False
        
        return True
    
    def _validate_list_result(
        self, 
        expected: List, 
        actual: List, 
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate list results (list_transactions)"""
        if len(expected) != len(actual):
            issues.append(
                f"❌ Result count mismatch: expected {len(expected)} transactions, "
                f"got {len(actual)}"
            )
            return False
        
        if len(actual) == 0:
            warnings.append("⚠️ Empty result set - may indicate over-filtering")
        
        # Validate structure of transactions
        for i, txn in enumerate(actual):
            if not isinstance(txn, dict):
                issues.append(f"❌ Transaction {i} is not a dict")
                return False
            
            required_keys = {"date", "amount", "category", "merchant"}
            if not required_keys.issubset(txn.keys()):
                issues.append(
                    f"❌ Transaction {i} missing required keys. "
                    f"Has {txn.keys()}, needs {required_keys}"
                )
                return False
        
        return True
    
    def _validate_dict_result(
        self, 
        expected: Dict, 
        actual: Dict, 
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate dict results (compare_periods)"""
        # Check keys match
        if set(expected.keys()) != set(actual.keys()):
            issues.append(
                f"❌ Result keys mismatch: expected {set(expected.keys())}, "
                f"got {set(actual.keys())}"
            )
            return False
        
        # Check values match (with tolerance for floats)
        for key in expected.keys():
            exp_val = expected[key]
            act_val = actual[key]
            
            if isinstance(exp_val, (int, float)):
                if abs(exp_val - act_val) > 0.01:
                    issues.append(
                        f"❌ Value mismatch for '{key}': "
                        f"expected {exp_val}, got {act_val}"
                    )
                    return False
            else:
                if exp_val != act_val:
                    issues.append(
                        f"❌ Value mismatch for '{key}': "
                        f"expected {exp_val}, got {act_val}"
                    )
                    return False
        
        return True
    
    def _validate_string_result(
        self, 
        expected: str, 
        actual: str, 
        issues: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate string results (top_category)"""
        if expected != actual:
            issues.append(
                f"❌ String result mismatch: expected '{expected}', got '{actual}'"
            )
            return False
        
        # Validate category exists
        if actual not in self.categories:
            warnings.append(
                f"⚠️ Result category '{actual}' not in dataset categories"
            )
        
        return True
    
    def _suggest_merchants(self, merchant: str, top_n: int = 3) -> List[str]:
        """Suggest similar merchants using fuzzy matching"""
        from rapidfuzz import fuzz
        
        scores = [
            (m, fuzz.ratio(merchant.lower(), m.lower())) 
            for m in self.merchants
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return [m for m, _ in scores[:top_n]]