import os
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
from PIL import Image
import pytesseract
# from deep_translator import GoogleTranslator
from gtts import gTTS
import requests
import pyttsx3
import pygame 
import shutil
from openai import OpenAI
import os
import json
import datetime


# TESSERACT CONFIGURATION
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class AITranslator:
    def __init__(self):
        self.lang_map = {
            'Auto-Detect': 'auto', 'English': 'en', 'Urdu': 'ur', 
            'Hindi': 'hi', 'Spanish': 'es', 'French': 'fr', 
            'German': 'de', 'Chinese': 'zh-CN', 'Arabic': 'ar'
        }
        pygame.mixer.init()

    def save_to_history(self, source_text, target_text, analysis_data):
        """Saves a translation record to a local JSON file."""
        history_file = "translation_history.json"
    
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = {
            "timestamp": timestamp,
            "source": source_text,
            "translation": target_text,
            "analysis": analysis_data
        }

        history = []
        # Check if the file exists and load existing data
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    history = []

        history.append(new_entry)
        
        # Save back to the file
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    def _execute_translation(self, text, src, tgt, custom_instruction):
        # Logic to skip synonyms for long text
        is_long = len(text.split()) > 30
        syn_instruction = "Return empty lists [] for synonyms/antonyms." if is_long else "Provide 3 synonyms and 3 antonyms."

        # DYNAMIC LANGUAGE RULES - STRICTLY ENFORCED
        src_rule = ""
        if src == "Urdu":
            src_rule = """
            CRITICAL LANGUAGE RULES FOR URDU SOURCE:
            1. ABSOLUTELY NO ENGLISH WORDS in any 'source_analysis' field.
            2. Structure analysis: Must be 100% Urdu script. Example: "یہ سادہ جملہ ہے۔" (CORRECT), NOT "This is a simple sentence."
            3. Grammar analysis: Must use ONLY Urdu grammatical terms:
               - Noun = اسم
               - Verb = فعل
               - Adjective = صفت
               - Adverb = حال
               - Subject = فاعل
               - Object = مفعول
               - Sentence = جملہ
               - Phrase = فقرہ
            4. Synonyms: List of Urdu words ONLY in Urdu script.
            5. Antonyms: List of Urdu words ONLY in Urdu script.
            6. Correction: If perfect, write ONLY "زبردست! ✅" - no English text.
            7. ZERO tolerance for language mixing in Urdu fields.
            """
        else:
            src_rule = f"""
            CRITICAL LANGUAGE RULES FOR {src.upper()} SOURCE:
            1. ABSOLUTELY NO MIXED LANGUAGES in any 'source_analysis' field.
            2. All analysis must be in {src} only.
            3. Structure, grammar, correction: Must use {src} language only.
            4. Synonyms: List of {src} words only.
            5. Antonyms: List of {src} words only.
            6. Correction: If perfect, write ONLY "Perfect! ✅" in {src}.
            """

        tgt_rule = ""
        if tgt == "Urdu":
            tgt_rule = """
            CRITICAL LANGUAGE RULES FOR URDU TARGET:
            1. ABSOLUTELY NO ENGLISH WORDS in any 'target_analysis' field.
            2. Structure analysis: Must be 100% Urdu script. Example: "اس جملے کی ساخت سادہ ہے۔"
            3. Grammar analysis: Must use ONLY Urdu grammatical terms:
               - Noun = اسم
               - Verb = فعل
               - Adjective = صفت
               - Adverb = حال
               - Subject = فاعل
               - Object = مفعول
               - Sentence = جملہ
               - Phrase = فقرہ
            4. Synonyms: List of Urdu words ONLY in Urdu script.
            5. Antonyms: List of Urdu words ONLY in Urdu script.
            6. ZERO tolerance for language mixing in Urdu fields.
            """
        else:
            tgt_rule = f"""
            CRITICAL LANGUAGE RULES FOR {tgt.upper()} TARGET:
            1. ABSOLUTELY NO MIXED LANGUAGES in any 'target_analysis' field.
            2. All analysis must be in {tgt} only.
            3. Structure, grammar: Must use {tgt} language only.
            4. Synonyms: List of {tgt} words only.
            5. Antonyms: List of {tgt} words only.
            """

        prompt = f"""
        {custom_instruction}
        
        Task: 
        1. Translate the Input Text from {src} to {tgt}.
           - **Translation Rule:** Translate naturally as a native speaker would say it.
           - **Avoid Definitions:** Do NOT define the sentence (e.g., "This means..."). Just translate it.
           - **Example:** If input is "My name is Ali", output "میرا نام علی ہے" (NOT "اسے میرا نام کہا جاتا ہے").

        2. Analyze the SOURCE text ({src}).
        3. Analyze the TARGET text ({tgt}).

        Input Text: "{text}"
        
        {syn_instruction}
        
        ==================== STRICT LANGUAGE ENFORCEMENT ====================
        {src_rule}
        {tgt_rule}
        =====================================================================
        
        STRUCTURE GUIDELINES:
    - Structure analysis MUST describe the full sentence, not individual words
    - Grammar analysis MUST be sentence-level, never word-level

    GRAMMAR ANALYSIS RULE (CRITICAL):
    - Do NOT analyze individual words separately
    - Identify فاعل، مفعول، فعل، زمانہ
    - If the sentence is idiomatic or metaphorical, analyze it as ONE unit

        IMPORTANT FOR URDU:
        - Use proper Urdu script (Nastaliq style)
        - Avoid Romanized Urdu (Urdu written in English letters)
        - Use proper Urdu punctuation
        
        JSON FIELD-SPECIFIC LANGUAGE RULES:
        1. For Urdu sections (source or target):
           - "structure": 100% Urdu script, NO English
           - "grammar": 100% Urdu script, NO English  
           - "correction": 100% Urdu script, NO English
           - "synonyms": List of Urdu words in Urdu script
           - "antonyms": List of Urdu words in Urdu script
           
        2. For English/non-Urdu sections:
           - All fields: 100% in that language, NO mixing
           
        3. The JSON keys ("structure", "grammar", etc.) stay in English.
           Only the VALUES change language based on rules above.
        
        FINAL CHECK: Before outputting, verify NO language mixing in any field.
        
        Strictly output this NESTED JSON structure:
        {{
            "translation": "The direct translated text",
            "source_analysis": {{
                "structure": "Analysis of sentence structure",
                "grammar": "Analysis of grammatical components",
                "correction": "Corrected text or 'Perfect! ✅' or 'زبردست! ✅'",
                "synonyms": ["List of synonyms in appropriate language"],
                "antonyms": ["List of antonyms in appropriate language"]
            }},
            "target_analysis": {{
                "structure": "Analysis of sentence structure",
                "grammar": "Analysis of grammatical components",
                "synonyms": ["List of synonyms in appropriate language"],
                "antonyms": ["List of antonyms in appropriate language"]
            }}
        }}
        
        ULTIMATE RULE: If analyzing Urdu text, use ZERO English words in any analysis field.
        """
        
        response = self.retry_api_call(prompt)
        result = self._parse_json(response.text)
        
        # Apply language validation to catch any remaining mixing
        return self._validate_language_purity(result, src, tgt)

    def ai_translate_with_metaphor(self, text, source_lang, target_lang):
        """Translates text by understanding metaphors and proverbs."""
        client = OpenAI(api_key="")

        prompt = f"""
        Act as an expert cultural translator. 
        If the input is an idiom or proverb (like 'Aa bail mujhe maar' or 'Piece of cake'), 
        do NOT translate word-for-word. Instead, provide the equivalent idiom or the 
        metaphorical meaning in {target_lang}.
        
        Source: {source_lang}
        Target: {target_lang}
        Text: "{text}"
        
        Return ONLY the translated text.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def get_detailed_analysis(self, text, lang="English"):
        """Uses AI to get real definitions, synonyms, and antonyms for any language."""
        client = OpenAI(api_key="")

        # We ask the AI for a JSON so we can parse it easily
        prompt = f"""
        Analyze this text: "{text}"
        Language: {lang}
        
        Return a JSON object with:
        1. "definition": A deep explanation of the phrase/metaphor (not word count).
        2. "synonyms": 3-5 related words or phrases in {lang}.
        3. "antonyms": 3-5 opposite words or phrases in {lang}.
        
        
        If it is a proverb, explain the cultural wisdom behind it.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" },
                temperature=0.3
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "definition": "Could not analyze text.",
                "synonyms": [],
                "antonyms": []
            }

    def resolve_metaphor(self, text):
        """
        Converts metaphors into plain literal meaning before translation.
        """
        metaphors = {
            "heart of stone": "emotionless and cold person",
            "time is money": "time is valuable",
            "break the ice": "start a conversation",
            "spill the beans": "reveal a secret",
            "burning the midnight oil": "working late at night",
            "piece of cake": "very easy task"
        }

        lowered = text.lower()
        for metaphor, meaning in metaphors.items():
            if metaphor in lowered:
                return text.lower().replace(metaphor, meaning)

        return text


    def get_supported_languages(self):
        """Returns the list of languages for the UI dropdowns."""
        return list(self.lang_map.keys())

    def set_volume(self, val):
        """Sets the playback volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(float(val))

    def stop_audio(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def play_audio_file(self, file_path):
        try:
            self.stop_audio() 
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except: pass

    def translate(self, text, src_lang, tgt_lang):
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator.\n"
                        "Translate idioms, metaphors, and phrases by MEANING.\n"
                        "Never translate word by word.\n"
                        "If text is an idiom, give its implied meaning."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
Source language: {src_lang}
Target language: {tgt_lang}

Text:
{text}
"""
                }
            ],
            temperature=0.1
        )

        return response.choices[0].message.content.strip()

    # def get_detailed_analysis(self, text):
    #     """Sentence-level grammar and structure analysis."""
    #     analysis = {
    #         'corrected': text,
    #         'target_word': "N/A",
    #         'definition': "N/A",
    #         'synonyms': [],
    #         'antonyms': []
    #     }

    #     if not text.strip(): 
    #         return analysis

    #     # Use the whole sentence for analysis
    #     analysis['target_word'] = text  # optional: main sentence as 'target_word'
    #     analysis['definition'] = f"Sentence length: {len(text.split())} words."

    #     # Fetch synonyms/antonyms for each word (optional: only non-stop words)
    #     words = [w.strip('.,!?;:').lower() for w in text.split()]
    #     stop_words = {'the', 'a', 'an', 'is', 'are', 'to', 'of', 'in', 'it', 'and', 'or', 'was'}
    #     filtered = [w for w in words if w not in stop_words and len(w) > 2]

    #     synonyms, antonyms = [], []
    #     for w in filtered:
    #         try:
    #             res = requests.get(f"https://api.datamuse.com/words?ml={w}&max=2").json()
    #             synonyms.extend([item['word'] for item in res])
    #             ant_res = requests.get(f"https://api.datamuse.com/words?rel_ant={w}&max=2").json()
    #             antonyms.extend([item['word'] for item in ant_res])
    #         except: 
    #             pass

    #     analysis['synonyms'] = list(set(synonyms))[:5]  # limit for readability
    #     analysis['antonyms'] = list(set(antonyms))[:5]

    #     # Grammar/Structure: simple rules
    #     analysis['structure'] = f"Sentence has {len(words)} words."
    #     analysis['grammar'] = "Sentence analyzed as a whole unit; subject, verb, object relationships preserved."

    #     return analysis


    def generate_audio(self, text, language, tone="Standard"):
        try:
            lang_code = self.lang_map.get(language, 'en')
            if tone == "Standard":
                tts = gTTS(text=text, lang=lang_code)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts.save(temp_file.name)
                temp_file.close()
                return temp_file.name

            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if tone == "Funny":
                engine.setProperty('rate', 350)
                if len(voices) > 1: engine.setProperty('voice', voices[1].id)
            elif tone == "Dramatic":
                engine.setProperty('rate', 85)
                if len(voices) > 0: engine.setProperty('voice', voices[0].id)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            engine.save_to_file(text, temp_file.name)
            engine.runAndWait()
            engine.stop()
            del engine
            return temp_file.name
        except: return None

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        try:
            fs, seconds = 44100, 5
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
            sd.wait()
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            write(temp_wav.name, fs, (myrecording * 32767).astype(np.int16))
            temp_wav.close()
            with sr.AudioFile(temp_wav.name) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
            os.unlink(temp_wav.name)
            return text
        except: return "Could not understand audio."

    def image_to_text(self, path):
        try:
            img = Image.open(path)
            return pytesseract.image_to_string(img).strip()
        except: return "Error: OCR failed."