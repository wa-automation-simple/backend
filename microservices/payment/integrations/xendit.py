"""Xendit Payment Gateway Integration"""
import httpx
from typing import Optional, Dict, Any
from ..core.config import settings


class XenditClient:
    """Client for interacting with Xendit Payment Gateway API"""
    
    def __init__(self):
        self.api_key = settings.XENDIT_SECRET_KEY
        self.base_url = settings.XENDIT_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.api_key}"
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Xendit API"""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    # Invoice Methods
    async def create_invoice(
        self,
        external_id: str,
        amount: int,
        payer_email: Optional[str] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        success_redirect_url: Optional[str] = None,
        failure_redirect_url: Optional[str] = None,
        items: Optional[list] = None,
        customer: Optional[Dict[str, Any]] = None,
        customer_notification_preference: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new invoice"""
        data = {
            "external_id": external_id,
            "amount": amount,
        }
        
        if payer_email:
            data["payer_email"] = payer_email
        if description:
            data["description"] = description
        if callback_url:
            data["callback_url"] = callback_url
        else:
            data["callback_url"] = settings.PAYMENT_CALLBACK_URL
        if success_redirect_url:
            data["success_redirect_url"] = success_redirect_url
        if failure_redirect_url:
            data["failure_redirect_url"] = failure_redirect_url
        if items:
            data["items"] = items
        if customer:
            data["customer"] = customer
        if customer_notification_preference:
            data["customer_notification_preference"] = customer_notification_preference
        
        return await self._request("POST", "/v2/invoices", data)
    
    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice by ID"""
        return await self._request("GET", f"/v2/invoices/{invoice_id}")
    
    async void_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Void an invoice"""
        return await self._request("POST", f"/invoices/{invoice_id}/void!")
    
    # Payment Method Methods
    async def get_payment_methods(self, types: Optional[str] = None) -> Dict[str, Any]:
        """Get available payment methods"""
        params = {}
        if types:
            params["types"] = types
        return await self._request("GET", "/payment_methods", params)
    
    async def create_payment_method(
        self,
        type: str,
        reusability: str,
        currency: str = "IDR",
        country: str = "ID",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment method token"""
        data = {
            "type": type,
            "reusability": reusability,
            "currency": currency,
            "country": country,
        }
        if metadata:
            data["metadata"] = metadata
        return await self._request("POST", "/payment_methods", data)
    
    # Virtual Account Methods
    async def create_fixed_va(
        self,
        external_id: str,
        bank_code: str,
        name: str,
        is_single_use: bool = False,
        suggested_amount: Optional[int] = None,
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a fixed virtual account"""
        data = {
            "external_id": external_id,
            "bank_code": bank_code,
            "name": name,
            "is_single_use": is_single_use,
        }
        if suggested_amount:
            data["suggested_amount"] = suggested_amount
        if expires_at:
            data["expires_at"] = expires_at
        if metadata:
            data["metadata"] = metadata
        return await self._request("POST", "/callback_urls", data)
    
    async def get_va_payment(self, external_id: str) -> Dict[str, Any]:
        """Get VA payment by external ID"""
        params = {"external_id": external_id}
        return await self._request("GET", "/pool/virtual_accounts", params)
    
    # Disbursement Methods
    async def create_disbursement(
        self,
        external_id: str,
        bank_code: str,
        account_holder_name: str,
        account_number: str,
        amount: int,
        description: str,
        email_to: Optional[list] = None
    ) -> Dict[str, Any]:
        """Create a disbursement (payout)"""
        data = {
            "external_id": external_id,
            "bank_code": bank_code,
            "account_holder_name": account_holder_name,
            "account_number": account_number,
            "amount": amount,
            "description": description,
        }
        if email_to:
            data["email_to"] = email_to
        return await self._request("POST", "/disbursements", data)
    
    async def get_disbursement(self, disbursement_id: str) -> Dict[str, Any]:
        """Get disbursement by ID"""
        return await self._request("GET", f"/disbursements/{disbursement_id}")
    
    # E-Wallet Methods
    async def create_ewallet_charge(
        self,
        external_id: str,
        currency: str,
        amount: int,
        checkout_method: str,
        channel_code: str,
        reference_id: str,
        customer_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create e-wallet charge"""
        data = {
            "external_id": external_id,
            "currency": currency,
            "amount": amount,
            "checkout_method": checkout_method,
            "channel_code": channel_code,
            "reference_id": reference_id,
        }
        if customer_id:
            data["customer_id"] = customer_id
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        return await self._request("POST", "/ewallets/charges", data)
    
    async def get_ewallet_charge(self, charge_id: str) -> Dict[str, Any]:
        """Get e-wallet charge by ID"""
        return await self._request("GET", f"/ewallets/charges/{charge_id}")


# Singleton instance
xendit_client = XenditClient()
