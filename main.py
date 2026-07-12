from flask import Flask
import telebot
import requests
import schedule
import time
import random
import threading
import io
from urllib.parse import quote

app = Flask(__name__)

# ===== НАСТРОЙКИ =====
BOT_TOKEN = '8733493942:AAE_ExnMmMXFccVUA-_P4II2Z9H9OUiWyV4'
AI_API_KEY = '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'
CHANNEL_ID = '-1004382108560'

bot = telebot.TeleBot(BOT_TOKEN)

# ===== ИИ ГЕНЕРАТОР ТЕКСТА =====
def generate_motivation():
    prompts = [
        "Напиши короткую мотивационную цитату на русском (2 предложения) про успех",
        "Создай вдохновляющий пост про преодоление трудностей (2-3 предложения) с эмодзи",
        "Напиши мотивационную мысль про целеустремленность (2 предложения)",
        "Создай пост про важность действий (2 предложения) с эмодзи 💪",
        "Напиши цитату про силу мышления (2 предложения)",
        "Напиши короткий пост про дисциплину и результат (2 предложения)",
        "Создай мотивацию для тех кто устал сдаваться (2 предложения) с эмодзи 🔥"
    ]
    
    prompt = random.choice(prompts)
    
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except:
        fallback = [
            "💪 Каждый день — новая возможность стать лучше. Действуй!",
            "🔥 Успех приходит к тем, кто не сдается!",
            "⭐ Твои мысли формируют реальность. Думай масштабно!",
            "🚀 Дисциплина — мост между целями и достижениями!",
            "💎 Препятствия — ступени к успеху!",
            "🎯 Фокус на цели, а не на проблемах. Двигайся вперед!",
            "💡 Великие дела начинаются с маленьких шагов. Начни сегодня!"
        ]
        return random.choice(fallback)

# ===== ГЕНЕРАТОР КАРТИНОК =====
def generate_image():
    """Генерирует мотивационную картинку через Pollinations.ai (бесплатно)"""
    try:
        themes = [
            "mountain sunrise golden light epic motivational",
            "ocean waves sunset peaceful inspirational",
            "forest path sunlight mystical success",
            "city skyline night stars achievement",
            "desert dunes sunset dramatic power",
            "snowy mountain peak clear sky freedom",
            "tropical beach paradise dream",
            "autumn forest golden leaves growth",
            "northern lights aurora sky magic",
            "space galaxy stars nebula infinite"
        ]
        
        theme = random.choice(themes)
        encoded_theme = quote(theme)
        
        image_url = f"https://image.pollinations.ai/prompt/{encoded_theme}?width=1080&height=1080&nologo=true&seed={random.randint(1, 99999)}"
        
        return image_url
    except:
        return None

# ===== ПОСТИНГ В КАНАЛ =====
def post_to_channel():
    if not CHANNEL_ID:
        print("❌ Не указан CHANNEL_ID")
        return
    
    content = generate_motivation()
    hashtags = "\n\n#мотивация #успех #саморазвитие #силамысли"
    full_text = content + hashtags
    
    image_url = generate_image()
    
    try:
        if image_url:
            # Скачиваем картинку
            print(f"📥 Скачиваю картинку...")
            img_response = requests.get(image_url, timeout=30)
            
            if img_response.status_code == 200:
                # Отправляем как файл
                photo = io.BytesIO(img_response.content)
                photo.name = 'motivation.jpg'
                bot.send_photo(CHANNEL_ID, photo, caption=full_text)
                print(f"✅ Пост с картинкой отправлен: {content[:50]}...")
            else:
                # Если не скачалась — отправляем только текст
                bot.send_message(CHANNEL_ID, full_text)
                print(f"✅ Пост (без картинки): {content[:50]}...")
        else:
            bot.send_message(CHANNEL_ID, full_text)
            print(f"✅ Пост (без картинки): {content[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# ===== РАСПИСАНИЕ (каждые 2 часа) =====
def run_schedule():
    schedule.every(2).hours.do(post_to_channel)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ===== ВЕБ-СЕРВЕР =====
@app.route('/')
def home():
    return "✅ Бот 'Сила Мысли' работает! Посты каждые 2 часа с картинками."

# ===== ЗАПУСК =====
thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

print("🚀 Бот запущен! Посты каждые 2 часа с картинками.")
try:
    post_to_channel()
except Exception as e:
    print(f"❌ Ошибка первого поста: {e}")
