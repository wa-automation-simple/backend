"""WhatsApp Service Integrations"""
from .playwright_client import WhatsAppAutomation, whatsapp_automation
from .selenium_client import WhatsAppSeleniumAutomation, whatsapp_selenium_automation

__all__ = [
    "WhatsAppAutomation",
    "whatsapp_automation",
    "WhatsAppSeleniumAutomation",
    "whatsapp_selenium_automation"
]
