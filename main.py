from flask import Flask
import telebot
import requests
import schedule
import time
import random
import threading
import os

app = Flask(__name__)

# ===== НАСТРОЙКИ =====
BOT_TOKEN ='8733493942:AAE_ExnMmMXFccVUA-_P4II2Z9H9OUiWyV4'
AI_API_KEY ='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'
CHANNEL_ID ='-1004382108560'


# ===== ИИ ГЕНЕРАТОР =====
def generate_motivation():
    prompts = [
        "Напиши короткую мотивационную цитату на русском (2 предложения) про успех",
        "Создай вдохновляющий пост про преодоление трудностей (2-3 предложения) с эмодзи",
        "Напиши мотивационную мысль про целеустремленность (2 предложения)",
        "Создай пост про важность действий (2 предложения) с эмодзи 💪",
        "Напиши цитату про силу мышления (2 предложения)"
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
            "💎 Препятствия — ступени к успеху!"
        ]
        return random.choice(fallback)

# ===== ПОСТИНГ =====
def post_to_channel():
    if not CHANNEL_ID:
        print("❌ Не указан CHANNEL_ID")
        return
    
    content = generate_motivation()
    hashtags = "\n\n#мотивация #успех #саморазвитие"
    full_text = content + hashtags
    
    try:
        bot.send_message(CHANNEL_ID, full_text)
        print(f"✅ Пост: {content[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# ===== РАСПИСАНИЕ =====
def run_schedule():
    schedule.every().day.at("09:00").do(post_to_channel)
    schedule.every().day.at("14:00").do(post_to_channel)
    schedule.every().day.at("20:00").do(post_to_channel)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ===== ВЕБ-СЕРВЕР =====
@app.route('/')
def home():
    return "✅ Бот 'Сила Мысли' работает!"

# ===== ЗАПУСК =====
if __name__ == "__main__":
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
    
    print("🚀 Запуск...")
    post_to_channel()
    
    app.run(host='0.0.0.0', port=8080)
