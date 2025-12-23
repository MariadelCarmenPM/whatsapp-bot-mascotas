from playwright.sync_api import sync_playwright
from src.config import Config
from src.pages.whatsapp_page import WhatsAppPage
from src.bot_logic import WhatsAppBot
import time

def main():
    print("------------------------------------------------")
    print(" WhatsApp Bot Iniciado - Presiona Ctrl+C para salir")
    print("------------------------------------------------")

    with sync_playwright() as p:
       
        browser_context = p.chromium.launch_persistent_context(
            user_data_dir=Config.USER_DATA_DIR, 
            headless=Config.HEADLESS,
            
          
            args=["--start-maximized"], 
            no_viewport=True          
            
        )
        
        
        if len(browser_context.pages) > 0:
            page = browser_context.pages[0]
        else:
            page = browser_context.new_page()

        whatsapp_page = WhatsAppPage(page)
        bot = WhatsAppBot(whatsapp_page)

       
        try:
            bot.run()
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido manualmente.")
        finally:
            browser_context.close()

if __name__ == "__main__":
    main()