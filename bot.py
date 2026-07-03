import logging
import json
import os
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ТОКЕН БОТА
BOT_TOKEN = "8980594233:AAG3PT1ZXxx3O1W7Zbn0StegJoP8NVBr7hg"

# ID АДМИНИСТРАТОРОВ
ADMIN_CHAT_IDS = [8439093137, 8560273220]

# НОМЕР ТЕЛЕФОНА ДЛЯ ОПЛАТЫ
PAYMENT_PHONE = "+79872353886"
PAYMENT_BANK = "Т-Банк"

# === ПРИВИЛЕГИИ ===
PRIVILEGES = {
    "knight": {"name": "🛡️ KNIGHT", "price": 20, "permanent": True},
    "prince": {"name": "👑 PRINCE", "price": 59, "permanent": True},
    "imperator": {"name": "⚔️ IMPERATOR", "price": 89, "permanent": True},
    "legend": {"name": "🌟 LEGEND", "permanent": False},
    "deluxe": {"name": "💎 DELUXE", "permanent": False},
    "extreme": {"name": "🔥 EXTREME", "permanent": False},
    "master": {"name": "🏆 MASTER", "permanent": False},
    "expert": {"name": "🧠 EXPERT", "permanent": False},
    "custom": {"name": "🎨 CUSTOM", "permanent": False},
    "sponsor": {"name": "🤝 SPONSOR", "permanent": False}
}

PRIVILEGE_PRICES = {
    "legend": {"1m": 100, "3m": 300, "forever": 450},
    "deluxe": {"1m": 250, "3m": 500, "forever": 750},
    "extreme": {"1m": 350, "3m": 700, "forever": 1050},
    "master": {"1m": 450, "3m": 900, "forever": 1350},
    "expert": {"1m": 550, "3m": 1100, "forever": 1650},
    "custom": {"1m": 750, "3m": 1500, "forever": 2250},
    "sponsor": {"1m": 950, "3m": 1900, "forever": 2850}
}

PRIVILEGE_EMOJIS = {
    "knight": "🛡️",
    "prince": "👑",
    "imperator": "⚔️",
    "legend": "🌟",
    "deluxe": "💎",
    "extreme": "🔥",
    "master": "🏆",
    "expert": "🧠",
    "custom": "🎨",
    "sponsor": "🤝"
}

SERVICES = {
    "razban": {"name": "🔓 Разбан", "price": 199},
    "razmut": {"name": "🔊 Размут", "price": 99}
}

CASES = {
    "donate_3": {"name": "🎁 Кейс с донатом 3шт", "price": 139},
    "donate_5": {"name": "🎁 Кейс с донатом 5шт", "price": 199},
    "donate_10": {"name": "🎁 Кейс с донатом 10шт", "price": 399},
    "megadonate_3": {"name": "💎 Кейс с мега донатом 3шт", "price": 199},
    "megadonate_5": {"name": "💎 Кейс с мега донатом 5шт", "price": 339},
    "megadonate_10": {"name": "💎 Кейс с мега донатом 10шт", "price": 579},
    "pounds_3": {"name": "💰 Кейс с фунтами 3шт", "price": 99},
    "pounds_5": {"name": "💰 Кейс с фунтами 5шт", "price": 269},
    "pounds_10": {"name": "💰 Кейс с фунтами 10шт", "price": 409},
    "currency_3": {"name": "🪙 Кейс с валютой 3шт", "price": 47},
    "currency_10": {"name": "🪙 Кейс с валютой 10шт", "price": 139},
    "currency_25": {"name": "🪙 Кейс с валютой 25шт", "price": 359},
    "spheres_3": {"name": "🌐 Кейс со сферами 3шт", "price": 69},
    "spheres_5": {"name": "🌐 Кейс со сферами 5шт", "price": 149},
    "spheres_10": {"name": "🌐 Кейс со сферами 10шт", "price": 249},
    "talismans_3": {"name": "🍀 Кейс с талисманами 3шт", "price": 59},
    "talismans_5": {"name": "🍀 Кейс с талисманами 5шт", "price": 109},
    "talismans_10": {"name": "🍀 Кейс с талисманами 10шт", "price": 169},
    "titles_3": {"name": "🏅 Кейс с титулами 3шт", "price": 39},
    "titles_5": {"name": "🏅 Кейс с титулами 5шт", "price": 79},
    "titles_10": {"name": "🏅 Кейс с титулами 10шт", "price": 109}
}

# Файлы для хранения данных
ORDERS_FILE = "orders.json"
PENDING_PAYMENTS_FILE = "pending_payments.json"
BLACKLIST_FILE = "blacklist.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def load_pending_payments():
    if os.path.exists(PENDING_PAYMENTS_FILE):
        with open(PENDING_PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_pending_payments(payments):
    with open(PENDING_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(payments, f, ensure_ascii=False, indent=2)

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(blacklist, f, ensure_ascii=False, indent=2)

# === ОСНОВНЫЕ КЛАВИАТУРЫ ===
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👑 Привилегии", callback_data="category_privileges")],
        [InlineKeyboardButton("🛠️ Услуги", callback_data="category_services")],
        [InlineKeyboardButton("🎁 Кейсы", callback_data="category_cases")],
        [InlineKeyboardButton("📋 Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton("📞 Связь с администрацией", callback_data="contact_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def privileges_keyboard():
    keyboard = []
    for key, item in PRIVILEGES.items():
        if item.get('permanent', False):
            keyboard.append([InlineKeyboardButton(
                f"{item['name']} - {item['price']}₽", 
                callback_data=f"buy_privilege_{key}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"{item['name']}", 
                callback_data=f"time_privilege_{key}"
            )])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def time_privilege_keyboard(privilege_key):
    prices = PRIVILEGE_PRICES.get(privilege_key, {})
    keyboard = [
        [InlineKeyboardButton(f"📅 1 месяц - {prices.get('1m', 0)}₽", callback_data=f"buy_privilege_{privilege_key}_1m")],
        [InlineKeyboardButton(f"📅 3 месяца - {prices.get('3m', 0)}₽", callback_data=f"buy_privilege_{privilege_key}_3m")],
        [InlineKeyboardButton(f"♾️ Навсегда - {prices.get('forever', 0)}₽", callback_data=f"buy_privilege_{privilege_key}_forever")],
        [InlineKeyboardButton("🔙 Назад", callback_data="category_privileges")]
    ]
    return InlineKeyboardMarkup(keyboard)

def services_keyboard():
    keyboard = []
    for key, item in SERVICES.items():
        keyboard.append([InlineKeyboardButton(f"{item['name']} - {item['price']}₽", callback_data=f"buy_service_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def cases_keyboard():
    keyboard = []
    for key, item in CASES.items():
        keyboard.append([InlineKeyboardButton(f"{item['name']} - {item['price']}₽", callback_data=f"buy_case_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

# === ОСНОВНЫЕ КОМАНДЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    
    # Проверка в черном списке
    blacklist = load_blacklist()
    if user.id in blacklist:
        await update.message.reply_text("🚫 Вы заблокированы в боте.")
        return
    
    logger.info(f"Пользователь {user.id} (@{user.username}) запустил бота")
    
    try:
        with open("image.png", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=(
                    f"🎮 <b>Добро пожаловать в магазин доната Saint Rose!</b>\n\n"
                    f"👋 Привет, {user.first_name}!\n"
                    f"Здесь ты можешь приобрести привилегии, услуги и кейсы.\n\n"
                    f"🛒 Выберите категорию:"
                ),
                parse_mode='HTML',
                reply_markup=main_menu_keyboard()
            )
    except:
        await update.message.reply_text(
            f"🎮 <b>Добро пожаловать в магазин доната Saint Rose!</b>\n\n"
            f"👋 Привет, {user.first_name}!\n"
            f"Здесь ты можешь приобрести привилегии, услуги и кейсы.\n\n"
            f"🛒 Выберите категорию:",
            parse_mode='HTML',
            reply_markup=main_menu_keyboard()
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # Проверка в черном списке
    blacklist = load_blacklist()
    if user_id in blacklist:
        await query.edit_message_text("🚫 Вы заблокированы в боте.")
        return
    
    logger.info(f"Кнопка нажата: {data}, пользователь: {user_id}")
    
    if data == "back_to_main":
        context.user_data.clear()
        await query.edit_message_text(
            "🛒 <b>Главное меню магазина</b>\n\nВыберите категорию:",
            parse_mode='HTML',
            reply_markup=main_menu_keyboard()
        )
        return
    
    if data == "category_privileges":
        await query.edit_message_text(
            "👑 <b>Привилегии</b>\n\n"
            "🟢 <i>KNIGHT, PRINCE, IMPERATOR - навсегда</i>\n"
            "🟡 <i>Остальные - с выбором времени</i>\n\n"
            "Выберите привилегию:",
            parse_mode='HTML',
            reply_markup=privileges_keyboard()
        )
        return
    
    if data == "category_services":
        await query.edit_message_text(
            "🛠️ <b>Услуги</b>\n\nВыберите услугу для покупки:",
            parse_mode='HTML',
            reply_markup=services_keyboard()
        )
        return
    
    if data == "category_cases":
        await query.edit_message_text(
            "🎁 <b>Кейсы</b>\n\nВыберите кейс для покупки:",
            parse_mode='HTML',
            reply_markup=cases_keyboard()
        )
        return
    
    if data == "my_orders":
        orders = load_orders()
        user_orders = [o for o in orders if o.get('user_id') == query.from_user.id]
        
        if not user_orders:
            await query.edit_message_text(
                "📋 У вас пока нет заказов.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])
            )
            return
        
        text = "📋 <b>Ваши заказы:</b>\n\n"
        for i, order in enumerate(user_orders[-10:], 1):
            status_emoji = "✅" if order.get('status') == "Выполнен" else "⏳"
            text += f"{i}. {order['item']}\n"
            text += f"   💰 {order['price']}₽\n"
            text += f"   {status_emoji} {order.get('status', 'Ожидает оплаты')}\n"
            text += f"   📅 {order['date']}\n\n"
        
        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])
        )
        return
    
    if data == "contact_admin":
        await query.edit_message_text(
            "📞 <b>Связь с администрацией</b>\n\n"
            "По всем вопросам обращайтесь:\n"
            "📱 Telegram: @union_with_apathy\n"
            "📱 Telegram: @noclip228\n\n"
            "Также вы можете написать /support",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])
        )
        return
    
    # Выбор времени для привилегии
    if data.startswith("time_privilege_"):
        privilege_key = data.replace("time_privilege_", "")
        privilege_name = PRIVILEGES.get(privilege_key, {}).get('name', '')
        
        await query.edit_message_text(
            f"⏰ <b>Выберите срок</b>\n\n"
            f"Привилегия: {privilege_name}\n\n"
            f"Выберите период:",
            parse_mode='HTML',
            reply_markup=time_privilege_keyboard(privilege_key)
        )
        return
    
    # Покупка привилегии навсегда
    if data.startswith("buy_privilege_") and "_" not in data.replace("buy_privilege_", ""):
        item_key = data.replace("buy_privilege_", "")
        item_data = PRIVILEGES.get(item_key)
        
        if not item_data:
            await query.edit_message_text("❌ Товар не найден.")
            return
        
        context.user_data['buy_item_key'] = item_key
        context.user_data['buy_item_name'] = item_data['name']
        context.user_data['buy_price'] = item_data['price']
        context.user_data['buy_category'] = 'privilege'
        context.user_data['buy_duration'] = 'навсегда'
        
        await query.edit_message_text(
            f"🛒 <b>Оформление заказа</b>\n\n"
            f"Товар: {item_data['name']}\n"
            f"Срок: навсегда\n"
            f"Цена: {item_data['price']}₽\n\n"
            f"📝 Введите ваш никнейм на сервере:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")]])
        )
        return
    
    # Покупка привилегии с временем
    if data.startswith("buy_privilege_") and "_" in data.replace("buy_privilege_", ""):
        parts = data.replace("buy_privilege_", "").split("_")
        if len(parts) == 2:
            item_key = parts[0]
            duration = parts[1]
            
            item_data = PRIVILEGES.get(item_key)
            if not item_data:
                await query.edit_message_text("❌ Товар не найден.")
                return
            
            prices = PRIVILEGE_PRICES.get(item_key, {})
            price = prices.get(duration, 0)
            
            duration_names = {"1m": "1 месяц", "3m": "3 месяца", "forever": "навсегда"}
            duration_name = duration_names.get(duration, duration)
            
            context.user_data['buy_item_key'] = item_key
            context.user_data['buy_item_name'] = f"{item_data['name']} ({duration_name})"
            context.user_data['buy_price'] = price
            context.user_data['buy_category'] = 'privilege'
            context.user_data['buy_duration'] = duration_name
            
            await query.edit_message_text(
                f"🛒 <b>Оформление заказа</b>\n\n"
                f"Товар: {item_data['name']}\n"
                f"Срок: {duration_name}\n"
                f"Цена: {price}₽\n\n"
                f"📝 Введите ваш никнейм на сервере:",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")]])
            )
            return
    
    # Покупка услуги
    if data.startswith("buy_service_"):
        item_key = data.replace("buy_service_", "")
        item_data = SERVICES.get(item_key)
        
        if not item_data:
            await query.edit_message_text("❌ Товар не найден.")
            return
        
        context.user_data['buy_item_key'] = item_key
        context.user_data['buy_item_name'] = item_data['name']
        context.user_data['buy_price'] = item_data['price']
        context.user_data['buy_category'] = 'service'
        context.user_data['buy_duration'] = '—'
        
        await query.edit_message_text(
            f"🛒 <b>Оформление заказа</b>\n\n"
            f"Товар: {item_data['name']}\n"
            f"Цена: {item_data['price']}₽\n\n"
            f"📝 Введите ваш никнейм на сервере:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")]])
        )
        return
    
    # Покупка кейса
    if data.startswith("buy_case_"):
        item_key = data.replace("buy_case_", "")
        item_data = CASES.get(item_key)
        
        if not item_data:
            await query.edit_message_text("❌ Товар не найден.")
            return
        
        context.user_data['buy_item_key'] = item_key
        context.user_data['buy_item_name'] = item_data['name']
        context.user_data['buy_price'] = item_data['price']
        context.user_data['buy_category'] = 'case'
        context.user_data['buy_duration'] = '—'
        
        await query.edit_message_text(
            f"🛒 <b>Оформление заказа</b>\n\n"
            f"Товар: {item_data['name']}\n"
            f"Цена: {item_data['price']}₽\n\n"
            f"📝 Введите ваш никнейм на сервере:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")]])
        )
        return
    
    # Подтверждение/отклонение заказа
    if data.startswith("confirm_") or data.startswith("reject_"):
        if user_id not in ADMIN_CHAT_IDS:
            await query.answer("❌ У вас нет прав!", show_alert=True)
            return
        
        action, order_id_str = data.split("_", 1)
        try:
            order_id = int(order_id_str)
        except ValueError:
            await query.answer("❌ Ошибка ID заказа", show_alert=True)
            return
        
        pending = load_pending_payments()
        order_data = None
        order_index = -1
        
        for i, p in enumerate(pending):
            if p.get('user_id') == order_id:
                order_data = p
                order_index = i
                break
        
        if not order_data:
            await query.message.reply_text("❌ Заказ не найден.")
            return
        
        if action == "confirm":
            orders = load_orders()
            orders.append({
                'user_id': order_data['user_id'],
                'username': order_data['username'],
                'nickname': order_data['nickname'],
                'item': order_data['item'],
                'price': order_data['price'],
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'Выполнен'
            })
            save_orders(orders)
            
            pending.pop(order_index)
            save_pending_payments(pending)
            
            await query.message.reply_text(
                f"✅ <b>Заказ подтвержден!</b>\n\n"
                f"👤 {order_data['nickname']}\n"
                f"🛒 {order_data['item']}\n"
                f"💰 {order_data['price']}₽\n\n"
                f"🎉 Товар выдан!",
                parse_mode='HTML'
            )
            
            try:
                await context.bot.send_message(
                    chat_id=order_data['user_id'],
                    text=f"✅ <b>Ваш заказ подтвержден!</b>\n\n"
                         f"🛒 {order_data['item']}\n"
                         f"💰 {order_data['price']}₽\n\n"
                         f"🎉 Товар выдан! Приятной игры!",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления игрока: {e}")
            
        elif action == "reject":
            pending.pop(order_index)
            save_pending_payments(pending)
            
            await query.message.reply_text(
                f"❌ <b>Заказ отклонен</b>\n\n"
                f"👤 {order_data['nickname']}\n"
                f"🛒 {order_data['item']}\n\n"
                f"Причина: чек не подтвержден.",
                parse_mode='HTML'
            )
            
            try:
                await context.bot.send_message(
                    chat_id=order_data['user_id'],
                    text=f"❌ <b>Ваш заказ отклонен</b>\n\n"
                         f"🛒 {order_data['item']}\n\n"
                         f"Причина: чек не подтвержден.\n"
                         f"Попробуйте оформить заказ заново.",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления игрока: {e}")
        
        return
    
    # Кнопка "Я оплатил, отправить чек"
    if data == "send_receipt":
        context.user_data['awaiting_receipt'] = True
        await query.edit_message_text(
            f"📸 <b>Отправка чека</b>\n\n"
            f"Отправьте скриншот чека об оплате.\n"
            f"Сумма: {context.user_data.get('buy_price', 0)}₽\n\n"
            f"📱 {PAYMENT_PHONE}\n"
            f"🏦 {PAYMENT_BANK}\n\n"
            f"❗️ <b>Важно!</b>\n"
            f"• Чек должен быть четким\n"
            f"• Сумма должна совпадать\n"
            f"• Дата оплаты должна быть сегодня\n\n"
            f"Отправьте фото чека:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")]])
        )
        return

async def handle_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ввода никнейма"""
    nickname = update.message.text.strip()
    
    # Проверка никнейма
    if len(nickname) < 3 or len(nickname) > 16:
        await update.message.reply_text("❌ Никнейм должен быть от 3 до 16 символов. Попробуйте снова:")
        return
    
    if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
        await update.message.reply_text("❌ Никнейм может содержать только буквы, цифры и _. Попробуйте снова:")
        return
    
    context.user_data['nickname'] = nickname
    
    item_name = context.user_data.get('buy_item_name')
    price = context.user_data.get('buy_price')
    duration = context.user_data.get('buy_duration', '')
    
    text = (
        f"✅ <b>Никнейм сохранен!</b>\n\n"
        f"🛒 {item_name}\n"
        f"💰 {price}₽\n"
        f"👤 {nickname}\n"
    )
    if duration and duration != '—':
        text += f"⏰ {duration}\n"
    text += (
        f"\n💳 <b>Реквизиты:</b>\n"
        f"📱 {PAYMENT_PHONE}\n"
        f"🏦 {PAYMENT_BANK}\n\n"
        f"⚠️ <b>Важно!</b>\n"
        f"1. Переведите ровно {price}₽\n"
        f"2. После оплаты нажмите кнопку ниже\n"
        f"3. Отправьте скриншот чека\n\n"
        f"⏳ После проверки администратор подтвердит заказ."
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Я оплатил, отправить чек", callback_data="send_receipt")],
        [InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка получения чека с проверкой"""
    if not context.user_data.get('awaiting_receipt'):
        await update.message.reply_text(
            "❌ Сначала выберите товар и нажмите 'Я оплатил'.\n"
            "Используйте /start",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 В меню", callback_data="back_to_main")]])
        )
        return
    
    if not update.message.photo:
        await update.message.reply_text("❌ Отправьте фото чека.")
        return
    
    # Сохраняем время отправки чека для проверки
    receipt_time = datetime.now()
    context.user_data['receipt_time'] = receipt_time.isoformat()
    
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    user = update.effective_user
    item_name = context.user_data.get('buy_item_name', 'Неизвестно')
    price = context.user_data.get('buy_price', 0)
    nickname = context.user_data.get('nickname', 'Не указан')
    
    # Сохраняем заказ
    pending = load_pending_payments()
    pending.append({
        'user_id': user.id,
        'username': user.username or user.first_name,
        'nickname': nickname,
        'item': item_name,
        'price': price,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'photo_file_id': file.file_id,
        'receipt_time': receipt_time.isoformat()
    })
    save_pending_payments(pending)
    
    # Отправка админам
    for admin_id in ADMIN_CHAT_IDS:
        try:
            caption = (
                f"🔔 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
                f"👤 {nickname}\n"
                f"🛒 {item_name}\n"
                f"💰 {price}₽\n"
                f"📱 @{user.username or 'не указан'}\n"
                f"🆔 {user.id}\n"
                f"⏰ {receipt_time.strftime('%H:%M:%S')}\n\n"
                f"✅ Проверьте чек!"
            )
            
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file.file_id,
                caption=caption,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{user.id}")],
                    [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")]
                ])
            )
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")
    
    await update.message.reply_text(
        f"✅ <b>Чек отправлен!</b>\n\n"
        f"🛒 {item_name}\n"
        f"💰 {price}₽\n\n"
        f"⏳ Ожидайте подтверждения (до 10 минут).\n\n"
        f"📞 Вопросы: @union_with_apathy или @noclip228",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛒 В меню", callback_data="back_to_main")]])
    )
    
    context.user_data.clear()

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📞 <b>Поддержка</b>\n\n"
        "📱 @union_with_apathy\n"
        "📱 @noclip228",
        parse_mode='HTML'
    )

# === АДМИН-КОМАНДЫ ===
async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return
    
    pending = load_pending_payments()
    
    if not pending:
        await update.message.reply_text("📋 Нет ожидающих заказов.")
        return
    
    text = "📋 <b>Ожидающие заказы:</b>\n\n"
    for i, order in enumerate(pending, 1):
        text += f"{i}. {order['item']} - {order['price']}₽\n"
        text += f"   👤 {order['nickname']}\n"
        text += f"   📱 @{order.get('username', 'не указан')}\n"
        text += f"   📅 {order['date']}\n\n"
    
    await update.message.reply_text(text, parse_mode='HTML')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return
    
    orders = load_orders()
    total = len(orders)
    total_sum = sum(o.get('price', 0) for o in orders)
    
    item_stats = {}
    for order in orders:
        item = order.get('item', 'Unknown')
        item_stats[item] = item_stats.get(item, 0) + 1
    
    stats_text = "📊 <b>Статистика</b>\n\n"
    stats_text += f"📦 Всего: {total}\n"
    stats_text += f"💰 Сумма: {total_sum}₽\n\n"
    
    stats_text += "<b>Топ товаров:</b>\n"
    sorted_items = sorted(item_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    for item, count in sorted_items:
        stats_text += f"• {item}: {count} шт.\n"
    
    await update.message.reply_text(stats_text, parse_mode='HTML')

async def admin_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Черный список"""
    if update.effective_user.id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return
    
    args = context.args
    if not args:
        blacklist = load_blacklist()
        if blacklist:
            await update.message.reply_text(f"🚫 Черный список: {blacklist}")
        else:
            await update.message.reply_text("🚫 Черный список пуст.")
        return
    
    action = args[0].lower()
    
    if action == "add" and len(args) > 1:
        try:
            user_id = int(args[1])
            blacklist = load_blacklist()
            if user_id not in blacklist:
                blacklist.append(user_id)
                save_blacklist(blacklist)
                await update.message.reply_text(f"✅ Пользователь {user_id} добавлен в черный список.")
            else:
                await update.message.reply_text(f"⚠️ Пользователь {user_id} уже в черном списке.")
        except ValueError:
            await update.message.reply_text("❌ Неверный ID пользователя.")
        return
    
    if action == "remove" and len(args) > 1:
        try:
            user_id = int(args[1])
            blacklist = load_blacklist()
            if user_id in blacklist:
                blacklist.remove(user_id)
                save_blacklist(blacklist)
                await update.message.reply_text(f"✅ Пользователь {user_id} удален из черного списка.")
            else:
                await update.message.reply_text(f"⚠️ Пользователь {user_id} не найден в черном списке.")
        except ValueError:
            await update.message.reply_text("❌ Неверный ID пользователя.")
        return
    
    await update.message.reply_text(
        "📋 <b>Черный список</b>\n\n"
        "/blacklist add <id> - добавить\n"
        "/blacklist remove <id> - удалить\n"
        "/blacklist - показать список",
        parse_mode='HTML'
    )

def main():
    """Запуск бота"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("support", support))
        application.add_handler(CommandHandler("admin", admin_orders))
        application.add_handler(CommandHandler("stats", admin_stats))
        application.add_handler(CommandHandler("blacklist", admin_blacklist))
        
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nickname))
        application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
        
        print("🚀 Бот запущен!")
        print(f"📱 Номер для оплаты: {PAYMENT_PHONE}")
        print(f"🏦 Банк: {PAYMENT_BANK}")
        print(f"👤 Админы: {ADMIN_CHAT_IDS}")
        print("📋 Всего товаров:")
        print(f"   👑 Привилегии: {len(PRIVILEGES)} шт. (3 навсегда, 7 с выбором времени)")
        print(f"   🛠️ Услуги: {len(SERVICES)} шт.")
        print(f"   🎁 Кейсы: {len(CASES)} шт.")
        print("Нажмите Ctrl+C для остановки")
        
        application.run_polling()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()