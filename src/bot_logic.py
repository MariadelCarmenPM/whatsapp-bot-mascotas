from src.pages.whatsapp_page import WhatsAppPage
from src.logger_config import get_logger
from src.database import init_db, registrar_venta
import time
import json
import os
import re  
from datetime import datetime

logger = get_logger(__name__)

class WhatsAppBot:
    def __init__(self, whatsapp_page: WhatsAppPage):
        self.wa = whatsapp_page
        self.state = {"step": "inicio", "data": {}, "carrito": []}
        
        init_db()

   
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, "productos.json") 
        self.precios = {} 
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.precios = json.load(f)
                logger.info("📚 Catálogo cargado correctamente.")
            else:
                logger.error("❌ No encuentro 'productos.json'.")
        except Exception as e:
            logger.error(f"❌ Error JSON: {e}")

    def obtener_menu_marcas(self):
        if not self.precios: return "⚠️ Error: Catálogo vacío."
        return "".join([f"🔹 *{m.capitalize()}*\n" for m in self.precios.keys()])

    def calcular_total_carrito(self):
        total = 0
        for item in self.state["carrito"]:
            total += item["subtotal"]
        return total

    def process_message(self, text: str) -> str:
        text_clean = text.lower().replace("\n", " ").strip()
        step = self.state["step"]
        
        logger.info(f"🧠 Step: {step} | Msg: {text_clean}")

        
        palabras_salida = ["salir", "cancelar", "ya no quiero", "adios", "chau", "bye", "fin"]
        
        if any(w in text_clean for w in palabras_salida) and step != "confirmar_salida":
            self.state["data"]["paso_anterior"] = step 
            self.state["step"] = "confirmar_salida"
            return "🤔 ¿Deseas cancelar todo el pedido y salir?\nResponde *SÍ* o *NO*."

        if step == "confirmar_salida":
            if any(w in text_clean for w in ["si", "sí", "yes", "claro"]):
                self.state = {"step": "inicio", "data": {}, "carrito": []} 
                return "👋 ¡Entendido! Pedido cancelado.\nArgosMarket te espera pronto. 🌟"
            elif any(w in text_clean for w in ["no", "regresar", "nop"]):
                paso_previo = self.state["data"].get("paso_anterior", "menu")
                self.state["step"] = paso_previo
                return "🎉 ¡Genial! Continuemos donde nos quedamos."
            else:
                return "No te entendí. Responde *SÍ* o *NO*."

  
        if step == "modo_humano":
            if any(w in text_clean for w in ["hola", "bot", "activar", "inicio"]):
                self.state["step"] = "menu"
                return f"🤖 *¡Bot reactivado!* 👇\n\n{self.obtener_menu_marcas()}"
            return None 

        if any(w in text_clean for w in ["asesor", "humano", "ayuda"]):
            self.state["step"] = "modo_humano"
            return "👨‍💻 *Modo Asesor.*\nEl bot guardará silencio. Escribe *HOLA* para reactivarlo."


        if any(w in text_clean for w in ["volver", "atras", "regresar"]):
            if step == "tipo":
                self.state["step"] = "menu"
                return f"🔄 *Volviendo...*\n👇 Elige una marca:\n\n{self.obtener_menu_marcas()}"
            elif step == "peso":
                self.state["step"] = "tipo"
                marca = self.state["data"].get("marca", "la marca")
                return f"🔄 *Corrigiendo etapa...*\n🐕 ¿*{marca.capitalize()}* para *Adulto* o *Cachorro*?"
            elif step == "cantidad":
                self.state["step"] = "peso"
                marca = self.state["data"].get("marca", "")
                tipo = self.state["data"].get("tipo", "")
                opciones = self.precios.get(marca, {}).get(tipo, {})
                texto = "\n".join([f"• *{k}* (S/ {v:.2f})" for k,v in opciones.items()])
                return f"🔄 *Corrigiendo peso...*\n📦 Precios {marca.capitalize()} {tipo}:\n{texto}\n\n👇 Elige el peso nuevamente."
            elif step == "nombre":
                 self.state["step"] = "agregar_mas"
                 return "🔄 *Volviendo al carrito...* ¿Deseas agregar algo más? (Sí/No)"
            else:
                self.state["step"] = "menu"
                return f"🔄 *Reiniciando...*\n👇 Elige una marca:\n\n{self.obtener_menu_marcas()}"

       
        saludos = ["hola", "buenas", "inicio", "menu", "start"]
        if any(s in text_clean for s in saludos):
            self.state = {"step": "menu", "data": {}, "carrito": []} 
            return (
                "¡Guau! 🐾 Bienvenido a *ArgosMarket Perú* 🇵🇪.\n"
                "Alimentos Premium a domicilio 🛵.\n\n"
                f"{self.obtener_menu_marcas()}\n"
                "──────────────\n"
                "✍️ Escribe *ASESOR* para ayuda humana."
            )


        if step == "menu":
            for marca in self.precios.keys():
                if marca in text_clean:
                    self.state["data"]["marca"] = marca
                    self.state["step"] = "tipo"
                    return f"👍 *{marca.capitalize()}*.\n¿Buscas *Adulto* o *Cachorro*?\n\n🔙 *VOLVER* para cambiar marca."
            return f"🤔 No entendí. Elige:\n{', '.join(self.precios.keys())}"

       
        elif step == "tipo":
            if "adult" in text_clean: self.state["data"]["tipo"] = "adulto"
            elif "cachorro" in text_clean: self.state["data"]["tipo"] = "cachorro"
            else: return "🐶 ¿Es para *Adulto* o *Cachorro*?"
            
            marca = self.state["data"]["marca"]
            tipo = self.state["data"]["tipo"]
            opciones = self.precios.get(marca, {}).get(tipo, {})
            
            if not opciones: return "⚠️ Sin stock. Escribe *VOLVER*."
            texto = "\n".join([f"• *{k}* (S/ {v:.2f})" for k,v in opciones.items()])
            self.state["step"] = "peso"
            return f"📦 Precios *{marca.capitalize()} {tipo}*:\n\n{texto}\n\n👇 Escribe el peso (ej: 15kg).\n🔙 *VOLVER* para cambiar etapa."

   
        elif step == "peso":
            marca, tipo = self.state["data"]["marca"], self.state["data"]["tipo"]
            opciones = self.precios.get(marca, {}).get(tipo, {})
            
            numeros_usuario = re.findall(r'\d+', text_clean)
            numero_elegido = numeros_usuario[0] if numeros_usuario else None
            peso_elegido = None
            
            if numero_elegido:
                for peso_db in opciones.keys():
                    numeros_db = re.findall(r'\d+', peso_db)
                    if numeros_db and numeros_db[0] == numero_elegido:
                        peso_elegido = peso_db
                        break
            
            if not peso_elegido:
                for p in opciones.keys():
                    if p in text_clean: peso_elegido = p; break

            if peso_elegido:
                self.state["data"]["peso"] = peso_elegido
                self.state["data"]["precio_unitario"] = opciones[peso_elegido]
                self.state["step"] = "cantidad"
                return (
                    f"✅ Entendido: {marca.capitalize()} {peso_elegido}.\n\n"
                    "🔢 *¿Cuántos sacos deseas llevar?*\n(Escribe el número, ej: 1, 2...)\n"
                    "🔙 *VOLVER* si te equivocaste de peso."
                )
            return "⚠️ No entendí el peso. Escribe el número exacto (ej: 2, 15)."

   
        elif step == "cantidad":
            numeros = re.findall(r'\d+', text_clean)
            if numeros:
                cantidad = int(numeros[0])
                if cantidad < 1: return "⚠️ La cantidad debe ser mayor a 0."
                
                item = {
                    "marca": self.state["data"]["marca"],
                    "tipo": self.state["data"]["tipo"],
                    "peso": self.state["data"]["peso"],
                    "precio": self.state["data"]["precio_unitario"],
                    "cantidad": cantidad,
                    "subtotal": self.state["data"]["precio_unitario"] * cantidad
                }
                self.state["carrito"].append(item)
                
                self.state["step"] = "agregar_mas"
                return (
                    f"🛒 *Agregado al carrito:*\n"
                    f"{cantidad}und x {item['marca'].capitalize()} {item['tipo']} ({item['peso']})\n"
                    f"💰 Subtotal item: S/ {item['subtotal']:.2f}\n\n"
                    f"💳 *Total Acumulado: S/ {self.calcular_total_carrito():.2f}*\n"
                    "──────────────────\n"
                    "🛍️ *¿Deseas agregar algo más?*\n"
                    "Responde *SÍ* para seguir comprando o *NO* para pagar."
                )
            else:
                return "🔢 No entendí la cantidad. Por favor escribe solo el número (ej: 1, 2)."

    
        elif step == "agregar_mas":
            if any(x in text_clean for x in ["si", "sí", "yes", "claro"]):
                self.state["step"] = "menu"
                return f"👍 ¡Vamos por más!\n\n{self.obtener_menu_marcas()}"
            elif any(x in text_clean for x in ["no", "nop", "pagar", "listo"]):
                self.state["step"] = "nombre"
                return "📝 ¡Perfecto! Para cerrar el pedido, indícame tu *Nombre y Apellido*."
            else:
                return "¿Deseas agregar otro producto? Responde *SÍ* o *NO*."

      
        elif step == "nombre":
            self.state["data"]["nombre"] = text.title()
            self.state["step"] = "direccion"
            return "📍 Indícame tu *Dirección y Distrito* de entrega."

        elif step == "direccion":
            self.state["data"]["direccion"] = text
            self.state["step"] = "pago"
            return "💳 ¿Pagarás con *Yape* o *Transferencia*?"

    
        elif step == "pago":
            
            metodo = None
            if "yape" in text_clean:
                metodo = "Yape"
            elif any(x in text_clean for x in ["transferencia", "transf", "cuenta", "bcp", "bbva"]):
                metodo = "Transferencia"
            
        
            if not metodo:
                return "⚠️ Método no válido.\nPor favor escribe *Yape* o *Transferencia* para finalizar."

        
            fecha = datetime.now().strftime("%d-%m-%Y %I:%M %p")
            
            detalle_productos = ""
            resumen_db = "" 
            
            for item in self.state["carrito"]:
                detalle_productos += f"🐶 {item['marca'].capitalize()} {item['tipo']} {item['peso']} | x{item['cantidad']} | S/ {item['subtotal']:.2f}\n"
                resumen_db += f"{item['marca']} {item['peso']}(x{item['cantidad']}), "

            total_pagar = self.calcular_total_carrito()
            
            datos_venta = {
                "nombre": self.state["data"]["nombre"],
                "marca": resumen_db.strip(", "),
                "tipo": "Varios",
                "peso": "Mix",
                "precio": total_pagar,
                "metodo_pago": metodo,
                "direccion": self.state["data"]["direccion"]
            }
            registrar_venta(datos_venta)
            
            self.state["carrito"] = []
            self.state = {"step": "fin", "data": {}, "carrito": []}
            
            return (
                "✅ *PEDIDO REGISTRADO* ✅\n"
                "──────────────────────\n"
                f"👤 {datos_venta['nombre']}\n" 
                f"{fecha}\n"
                "──────────────────────\n"
                f"{detalle_productos}"
                "──────────────────────\n"
                f"💰 *Total a Pagar: S/ {total_pagar:.2f}*\n"
                f"📍 {datos_venta['direccion']}\n" 
                f"💳 {metodo}\n"
                "──────────────────────\n"
                "🛵 *Tu pedido ha sido enviado a almacén.*\n"
                "      🐶 ArgosMarket 🦴"
            )

        return "Ups, no entendí. Escribe *MENU*."

    def run(self):
        self.wa.navigate()
        try: self.wa.wait_for_login()
        except: pass
        logger.info("🤖 BOT ACTIVO SISTEMA ARGOS")
        
        while True:
            try:
                unread = self.wa.get_unread_chats()
                if unread:
                    self.wa.open_chat_by_locator(unread[0])
                    intentos = 0
                    while intentos < 20:
                        msg = self.wa.get_last_message_text()
                        if msg:
                            resp = self.process_message(msg)
                            if resp: self.wa.send_message(resp)
                            
                            if self.state["step"] == "fin":
                                time.sleep(2)
                                self.state["step"] = "inicio"
                                break
                            
                            intentos = 0
                            time.sleep(3)
                        else:
                            time.sleep(2)
                            intentos += 1
                else:
                    time.sleep(2)
            except KeyboardInterrupt: break
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(5)