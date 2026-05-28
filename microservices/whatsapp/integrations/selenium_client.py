"""WhatsApp Browser Automation using Selenium (Alternative)"""
import time
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException


class WhatsAppSeleniumAutomation:
    """WhatsApp Web automation using Selenium"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    def start(self):
        """Start browser and open WhatsApp Web"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        # Initialize Chrome driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://web.whatsapp.com")
        self.wait = WebDriverWait(self.driver, 60)
        
        return self
    
    def wait_for_qr_scan(self, timeout: int = 60) -> bool:
        """Wait for QR code to be scanned"""
        try:
            # Wait for main chat container to appear (indicates successful login)
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[data-testid="chat-list"]')
                )
            )
            return True
        except TimeoutException:
            raise TimeoutError("QR code scan timeout")
    
    def send_message(self, phone_number: str, message: str) -> bool:
        """Send a message to a phone number"""
        try:
            # Navigate to chat
            url = f"https://web.whatsapp.com/send?phone={phone_number}"
            self.driver.get(url)
            
            # Wait for message input box
            time.sleep(3)  # Allow page to load
            message_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
                )
            )
            
            # Type message
            message_box.clear()
            message_box.send_keys(message)
            time.sleep(0.5)
            
            # Press Enter to send
            from selenium.webdriver.common.keys import Keys
            message_box.send_keys(Keys.ENTER)
            
            # Wait for message to be sent
            time.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def send_message_by_name(self, contact_name: str, message: str) -> bool:
        """Send a message to a contact by name"""
        try:
            # Click on search box
            search_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="3"]')
                )
            )
            search_box.click()
            search_box.clear()
            search_box.send_keys(contact_name)
            time.sleep(1)
            
            # Click on first result
            result = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[role="listitem"]')
                )
            )
            result.click()
            
            # Send message
            return self._send_message_to_current_chat(message)
        except Exception as e:
            print(f"Error sending message by name: {str(e)}")
            return False
    
    def _send_message_to_current_chat(self, message: str) -> bool:
        """Send message to currently open chat"""
        try:
            message_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
                )
            )
            message_box.clear()
            message_box.send_keys(message)
            time.sleep(0.5)
            
            from selenium.webdriver.common.keys import Keys
            message_box.send_keys(Keys.ENTER)
            time.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def get_unread_messages(self) -> List[Dict[str, Any]]:
        """Get unread messages from current chat"""
        try:
            messages = []
            unread_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 'span[data-testid="unread-msg-count"]'
            )
            
            for element in unread_elements:
                count = element.text
                messages.append({"count": count})
            
            return messages
        except Exception as e:
            print(f"Error getting unread messages: {str(e)}")
            return []
    
    def get_chat_list(self) -> List[Dict[str, Any]]:
        """Get list of recent chats"""
        try:
            chats = []
            chat_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 'div[role="listitem"]'
            )
            
            for i, chat in enumerate(chat_elements[:10]):  # Limit to 10 chats
                try:
                    name_element = chat.find_element(By.CSS_SELECTOR, 'span[dir="auto"]')
                    name = name_element.text if name_element else "Unknown"
                    
                    chats.append({
                        "index": i,
                        "name": name
                    })
                except:
                    continue
            
            return chats
        except Exception as e:
            print(f"Error getting chat list: {str(e)}")
            return []
    
    def is_logged_in(self) -> bool:
        """Check if WhatsApp Web is logged in"""
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[data-testid="chat-list"]')
                ),
                timeout=5
            )
            return True
        except:
            return False
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()


# Singleton instance
whatsapp_selenium_automation = WhatsAppSeleniumAutomation()
