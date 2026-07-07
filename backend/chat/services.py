import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings

# Use a safe path for .env
env_path = Path('c:/Users/Asus/Desktop/antigravity/backend/.env')
load_dotenv(env_path)

from vehicles.models import get_gemini_api_key

class ChatService:
    def __init__(self):
        self.connected = False
        try:
            api_key = get_gemini_api_key()
            if api_key:
                genai.configure(api_key=api_key)
                self.system_instruction = """Siz "Smart Baholash" dasturining universal va professional AI yordamchisiz. 

Muloqot qoidalari:
1. Inson kabi tabiiy, samimiy va juda chiroyli tilda javob bering. Quruq va robotdek gapirmang.
2. Agar foydalanuvchi salom bersa yoki oddiy hol-ahvol so'rasa, albatta alik oling va juda samimiy munosabatda bo'ling.
3. Suhbat davomida har bir xabarda "Salom" deb takrorlamang, lekin boshida albatta salomlashish shart.
4. O'zbek tili grammatikasi va imlosiga qat'iy rioya qiling. 
5. Matematika, biznes, ta'lim va boshqa sohalarda mukkammal va aqlli yordam bering.
6. Agar savol baholash sohasiga oid bo'lsa, platformadagi bilimlaringizdan (context) foydalanib eng aniq ma'lumotlarni bering. Agar context savolga aloqador bo'lmasa, uni e'tiborsiz qoldiring.
7. O'zingizni "Smart Yordamchi" deb tanishtiring.
"""
                self.safety_settings = {
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                }
                
                # Initialize ChromaDB safely
                try:
                    import chromadb
                    db_path = str(Path(settings.BASE_DIR) / 'chroma_db')
                    self.chroma_client = chromadb.PersistentClient(path=db_path)
                    self.collection = self.chroma_client.get_or_create_collection(name="evaluation_books")
                except Exception as ce:
                    print(f"ChromaDB Load Error: {ce}")
                    self.collection = None
                
                self.connected = True
            else:
                print("ERROR: GEMINI_API_KEY is missing from DB and .env")
        except Exception as e:
            print(f"Gemini/Chroma Init Error: {e}")



    def get_context(self, query):
        """Retrieve relevant context from ChromaDB."""
        try:
            if not hasattr(self, 'collection') or self.collection is None:
                return ""
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            if results and results['documents'] and results['documents'][0]:
                context = "\n".join(results['documents'][0])
                return context
            return ""
        except Exception as e:
            print(f"Context retrieval error: {e}")
            return ""

    def get_chat_response(self, message, history=None, image_data=None, image_mime_type=None):
        """Generates a response using history, retrieved context, and optional image."""
        if not self.connected:
            return "Kechirasiz, hozir AI tizimiga ulanishda muammo bor. API kalitini tekshiring."

        try:
            # 1. Get Context from ChromaDB (only if no image, or as supplement)
            context = self.get_context(message)
            
            # 2. Prepare History for Gemini (role mapping)
            gemini_history = []
            if history:
                # Limit history to last 10 messages for stability
                for msg in history[-10:]:
                    role = "user" if msg['role'] == 'user' else "model"
                    gemini_history.append({"role": role, "parts": [msg['content']]})

            # 3. Construct Content Parts
            content_parts = []
            
            prompt = message
            
            # Greetings detection (simple list)
            greetings = ['salom', 'hello', 'assalom', 'qalaysiz', 'ishlar', 'hi', 'yaxshimisiz', 'salomalik']
            is_greeting = any(g in message.lower() for g in greetings)
            
            if context and not is_greeting:
                prompt = f"Bilimlar bazasidagi ma'lumot (agar savolga aloqador bo'lsa foydalaning):\n{context}\n\nFoydalanuvchi xabari: {message}"
            
            content_parts.append(prompt)
            
            if image_data and image_mime_type:
                content_parts.append({
                    "mime_type": image_mime_type,
                    "data": image_data
                })

            # Try gemini-3.5-flash first, then gemini-2.5-flash, then gemini-2.0-flash with retries on 429
            models_to_try = ['models/gemini-3.5-flash', 'models/gemini-2.5-flash', 'models/gemini-2.0-flash']
            response = None
            last_err = None

            for model_name in models_to_try:
                for attempt in range(3):
                    try:
                        model = genai.GenerativeModel(
                            model_name,
                            system_instruction=self.system_instruction,
                            safety_settings=self.safety_settings
                        )
                        chat = model.start_chat(history=gemini_history)
                        print(f"DEBUG: sending to Gemini model {model_name} (multimodal: {bool(image_data)})...")
                        res = chat.send_message(
                            content_parts,
                            generation_config=genai.types.GenerationConfig(
                                max_output_tokens=4096,
                                temperature=0.7
                            )
                        )
                        res.resolve()
                        response = res
                        break
                    except Exception as e:
                        last_err = e
                        err_str = str(e).lower()
                        if "429" in err_str or "resourceexhausted" in err_str or "quota" in err_str:
                            print(f"RATE LIMIT (429) hit on model {model_name}. Retrying in {1.5 * (attempt + 1)}s...")
                            import time
                            time.sleep(1.5 * (attempt + 1))
                            continue
                        else:
                            raise e
                if response:
                    break

            if response and response.text:
                return response.text
            else:
                if last_err:
                    raise last_err
                return "AI javob qaytara olmadi. Iltimos, qaytadan urinib ko'ring."
                
        except Exception as e:
            print(f"CHAT SERVICE CRITICAL: {str(e)}")
            return f"Xatolik yuz berdi: {str(e)}"
