from playwright.sync_api import Page, Locator
from src.logger_config import get_logger
import time

logger = get_logger(__name__)

class WhatsAppPage:
    def __init__(self, page: Page):
        self.page = page
        self.message_box = 'div[contenteditable="true"][data-tab="10"]'

    def navigate(self):
        logger.info("Navegando a WhatsApp Web...")
        self.page.goto("https://web.whatsapp.com/")
        
    def wait_for_login(self):
        logger.info("Esperando inicio de sesión...")
        try:
            self.page.wait_for_selector("#pane-side", timeout=60000)
            logger.info("¡Sesión iniciada correctamente!")
        except Exception:
            logger.error("No se detectó el inicio de sesión.")
            raise

    def get_unread_chats(self) -> list[Locator]:
        """
        ESTRATEGIA NUCLEAR (XPath):
        Busca específicamente el icono verde o el texto de 'no leído' en cualquier nivel.
        """
        try:
            # Opción 1: Buscar por el atributo aria-label que contenga "no leído" (Español) o "unread" (Inglés)
            xpath_label = '//*[@id="pane-side"]//*[contains(@aria-label, "no leído") or contains(@aria-label, "unread")]'
            
            # Opción 2: Buscar el circulito verde por su color (a veces útil si el texto falla)
            # (Omitido por ahora para no complicar, el XPath de texto suele ser infalible)

            chats = self.page.locator(xpath_label).all()
            
            # FILTRO DE SEGURIDAD:
            # A veces trae elementos duplicados. Filtramos solo los visibles.
            valid_chats = [c for c in chats if c.is_visible()]

            if len(valid_chats) > 0:
                print(f"DEBUG -> ¡ENCONTRÉ {len(valid_chats)} CHATS VERDES! (Usando XPath)")
                return valid_chats
            
            return []
        except Exception as e:
            return []

    def open_chat_by_locator(self, badge_locator: Locator):
        """Abre el chat haciendo clic forzado."""
        try:
            # Intentamos hacer clic en el elemento encontrado
            badge_locator.click(force=True)
            self.page.wait_for_timeout(1000) # Espera a que cargue la derecha
        except Exception as e:
            logger.error(f"Error al abrir chat: {e}")

    def get_last_message_text(self) -> str:
        time.sleep(1.0) # Un poco más rápido
        
        messages = self.page.locator('div[role="row"]')
        count = messages.count()

        if count == 0:
            return ""

        last_msg = messages.nth(count - 1)

        # Si el mensaje es mío (message-out), retorno vacío
        if last_msg.locator(".message-out").count() > 0:
            return ""

        text_element = last_msg.locator("span.selectable-text").first
        
        if text_element.is_visible():
            return text_element.inner_text().strip()
            
        return last_msg.inner_text().strip()

    def send_message(self, text: str):
        try:
            box = self.page.locator(self.message_box)
            box.click()
            box.fill(text)
            self.page.keyboard.press("Enter")
            logger.info(f"Mensaje enviado.")
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")