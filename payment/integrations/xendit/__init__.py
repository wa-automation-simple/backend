"""Xendit Payment Gateway Integration"""
import os
import requests
from typing import Optional, Dict, Any

XENDIT_SECRET_KEY = os.getenv("XENDIT_SECRET_KEY", "xnd_development_xxx")
XENDIT_BASE_URL = "https://api.xendit.co"

class XenditClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or XENDIT_SECRET_KEY
        self.base_url = XENDIT_BASE_URL
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice"""
        response = requests.post(
            f"{self.base_url}/v2/invoices",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice by ID"""
        response = requests.get(
            f"{self.base_url}/v2/invoices/{invoice_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_payment_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment request"""
        response = requests.post(
            f"{self.base_url}/payment-requests",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def create_disbursement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create disbursement (payout)"""
        response = requests.post(
            f"{self.base_url}/disbursements",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
