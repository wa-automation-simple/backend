"""WhatsApp Browser Automation using Playwright"""
import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from ..config import settings


class WhatsAppAutomation:
    """WhatsApp Web automation using Playwright"""
    
    def __init__(self):
        self.browser_type = settings.BROWSER_TYPE
        self.headless = settings.HEADLESS
        self.timeout = settings.BROWSER_TIMEOUT
        self.session_path = settings.SESSION_PATH
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start(self):
        """Start browser and open WhatsApp Web"""
        playwright = await async_playwright().start()
        
        # Launch browser based on type
        if self.browser_type == "firefox":
            self.browser = await playwright.firefox.launch(
                headless=self.headless
            )
        elif self.browser_type == "webkit":
            self.browser = await playwright.webkit.launch(
                headless=self.headless
            )
        else:  # chromium (default)
            self.browser = await playwright.chromium.launch(
                headless=self.headless
            )
        
        # Create context with storage state for session persistence
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        self.page = await self.context.new_page()
        await self.page.goto("https://web.whatsapp.com", timeout=self.timeout)
        
        return self
    
    async def wait_for_qr_scan(self, timeout: int = 60000):
        """Wait for QR code to be scanned"""
        try:
            # Wait for main chat container to appear (indicates successful login)
            await self.page.wait_for_selector(
                'div[data-testid="chat-list"]',
                timeout=timeout
            )
            return True
        except Exception as e:
            raise TimeoutError(f"QR code scan timeout: {str(e)}")
    
    async def send_message(self, phone_number: str, message: str) -> bool:
        """Send a message to a phone number"""
        try:
            # Navigate to chat
            url = f"https://web.whatsapp.com/send?phone={phone_number}"
            await self.page.goto(url, timeout=self.timeout)
            
            # Wait for message input box
            await asyncio.sleep(2)  # Allow page to load
            message_box = await self.page.wait_for_selector(
                'div[contenteditable="true"][data-tab="10"]',
                timeout=10000
            )
            
            # Type message
            await message_box.fill(message)
            await asyncio.sleep(0.5)
            
            # Press Enter to send
            await message_box.press("Enter")
            
            # Wait for message to be sent
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    async def send_message_by_name(self, contact_name: str, message: str) -> bool:
        """Send a message to a contact by name"""
        try:
            # Click on search box
            search_box = await self.page.wait_for_selector(
                'div[contenteditable="true"][data-tab="3"]',
                timeout=10000
            )
            await search_box.click()
            await search_box.fill(contact_name)
            await asyncio.sleep(1)
            
            # Click on first result
            result = await self.page.wait_for_selector(
                'div[role="listitem"]',
                timeout=5000
            )
            await result.click()
            
            # Send message
            return await self._send_message_to_current_chat(message)
        except Exception as e:
            print(f"Error sending message by name: {str(e)}")
            return False
    
    async def _send_message_to_current_chat(self, message: str) -> bool:
        """Send message to currently open chat"""
        try:
            message_box = await self.page.wait_for_selector(
                'div[contenteditable="true"][data-tab="10"]',
                timeout=10000
            )
            await message_box.fill(message)
            await asyncio.sleep(0.5)
            await message_box.press("Enter")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    async def get_unread_messages(self) -> List[Dict[str, Any]]:
        """Get unread messages from current chat"""
        try:
            messages = []
            # Find unread message indicators
            unread_elements = await self.page.query_selector_all(
                'span[data-testid="unread-msg-count"]'
            )
            
            for element in unread_elements:
                count = await element.inner_text()
                messages.append({"count": count})
            
            return messages
        except Exception as e:
            print(f"Error getting unread messages: {str(e)}")
            return []
    
    async def get_chat_list(self) -> List[Dict[str, Any]]:
        """Get list of recent chats"""
        try:
            chats = []
            chat_elements = await self.page.query_selector_all(
                'div[role="listitem"]'
            )
            
            for i, chat in enumerate(chat_elements[:10]):  # Limit to 10 chats
                try:
                    name_element = await chat.query_selector('span[dir="auto"]')
                    name = await name_element.inner_text() if name_element else "Unknown"
                    
                    time_element = await chat.query_selector('span[data-testid="chat-meta"]')
                    time = await time_element.inner_text() if time_element else ""
                    
                    chats.append({
                        "index": i,
                        "name": name,
                        "last_message_time": time
                    })
                except:
                    continue
            
            return chats
        except Exception as e:
            print(f"Error getting chat list: {str(e)}")
            return []
    
    async def save_session(self, path: Optional[str] = None):
        """Save current session state"""
        if self.context:
            storage_state = await self.context.storage_state()
            save_path = path or f"{self.session_path}/whatsapp_session.json"
            import json
            with open(save_path, 'w') as f:
                json.dump(storage_state, f)
    
    async def load_session(self, path: Optional[str] = None):
        """Load session state from file"""
        import json
        import os
        
        load_path = path or f"{self.session_path}/whatsapp_session.json"
        
        if os.path.exists(load_path):
            with open(load_path, 'r') as f:
                storage_state = json.load(f)
            
            if self.context:
                await self.context.add_cookies(storage_state.get("cookies", []))
                return True
        
        return False
    
    async def is_logged_in(self) -> bool:
        """Check if WhatsApp Web is logged in"""
        try:
            await self.page.wait_for_selector(
                'div[data-testid="chat-list"]',
                timeout=5000
            )
            return True
        except:
            return False
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()


# Singleton instance
whatsapp_automation = WhatsAppAutomation()
