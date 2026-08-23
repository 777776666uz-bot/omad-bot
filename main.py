import asyncio
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

# Бот ва тўлов токенлари
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8849345672:AAEaKO6YYMyKCoGvS2XrDdRDLIvOoM03LnA"
PAYMENT_TOKEN = os.environ.get("PAYMENT_TOKEN", "398062629:TEST:99999999_f50bb3b37803e1e4")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 4 та маҳсулот маълумотлари (нархлари 10 000 - 12 000 сўм)
PRODUCTS = {
    "aurum_shelf": {
        "title": "«Aurum» премиум стеллажи",
        "desc": (
            "✨ <b>«Aurum»</b> — премиум стеллаж!\n\n"
            "📐 <b>Ўлчамлари:</b> 180 x 80 x 30 см\n"
            "🛠 <b>Каркас:</b> Мустаҳкам металл профил (олтинранг)\n"
            "🗄 <b>Жавонлар:</b> Премиум ЛДСП/МДФ\n"
            "💎 <b>Услуб:</b> Modern, Loft, Neoclassic"
        ),
        "price": 10000,
        "max_tickets": 500,
        "current_ticket": 1
    },
    "vogue_rack": {
        "title": "«Vogue Rack» премиум гардероб",
        "desc": (
            "✨ <b>«Vogue Rack»</b> — LED ёритгичли гардероб вешалкаси!\n\n"
            "📐 <b>Ўлчамлари:</b> 180 x 120 x 40 см\n"
            "💡 <b>Хусусиятлар:</b> Ички LED ёритгич, кенг осма жой ва 4 қаватли жавонлар\n"
            "🛠 <b>Каркас:</b> Мустаҳкам металл профиль"
        ),
        "price": 12000,
        "max_tickets": 400,
        "current_ticket": 1
    },
    "veragold_console": {
        "title": "«Veragold» премиум консол столи",
        "desc": (
            "✨ <b>«Veragold»</b> — Премиум консол столи!\n\n"
            "📐 <b>Ўлчамлари:</b> 115 x 85 x 30 см\n"
            "🏛 <b>Столешница:</b> Мармар кўринишидаги сифатли ЛМДФ\n"
            "🛠 <b>Каркас:</b> Зарҳал (Gold) металл профиль (20х20 мм)\n"
            "💎 <b>Услуб:</b> Neoclassic, Luxury Loft"
        ),
        "price": 10000,
        "max_tickets": 350,
        "current_ticket": 1
    },
    "avva_console": {
        "title": "«AVVA» консоль столи",
        "desc": (
            "✨ <b>«AVVA»</b> — Премиум консоль столи!\n\n"
            "📐 <b>Ўлчамлари:</b> 1300 x 380 x 820 мм\n"
            "🪞 <b>Юз қисми:</b> Тобланган тиниқ ойна (Tempered Glass)\n"
            "🛠 <b>Каркас:</b> Зангламайдиган пўлат / зарҳал профиль\n"
            "💎 <b>Услуб:</b> Neoclassic / Modern Luxury"
        ),
        "price": 12000,
        "max_tickets": 450,
        "current_ticket": 1
    }
}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    text = (
        f"👋 Ассалому алайкум, <b>{message.from_user.first_name}</b>!\n\n"
        f"🎁 <b>Ютуқли премиум мебеллар акциясига хуш келибсиз!</b>\n\n"
        f"Иштирок этиш учун совринни танланг:"
    )
    buttons = []
    for p_id, p_data in PRODUCTS.items():
        left = p_data["max_tickets"] - p_data["current_ticket"] + 1
        buttons.append([types.InlineKeyboardButton(
            text=f"✨ {p_data['title']} — {p_data['price']:,} сўм ({left} та қолди)",
            callback_data=f"sel_{p_id}"
        )])
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("sel_"))
async def select_product_handler(callback: types.CallbackQuery):
    p_id = callback.data.replace("sel_", "")
    p_data = PRODUCTS.get(p_id)
    if not p_data:
        return
    left = p_data["max_tickets"] - p_data["current_ticket"] + 1
    
    text = (
        f"{p_data['desc']}\n\n"
        f"🎟 <b>1 та чипта нархи:</b> {p_data['price']:,} сўм\n"
        f"📊 <b>Қолган чипталар:</b> {left} та"
    )
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎟 Чипта сотиб олиш", callback_data=f"pay_{p_id}")],
        [types.InlineKeyboardButton(text="⬅️ Ортга қайтиш", callback_data="back_cat")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "back_cat")
async def back_cat_handler(callback: types.CallbackQuery):
    await start_handler(callback.message)

@dp.callback_query(F.data.startswith("pay_"))
async def invoice_handler(callback: types.CallbackQuery):
    p_id = callback.data.replace("pay_", "")
    p_data = PRODUCTS.get(p_id)
    if not p_data:
        return

    amount_tiyin = p_data["price"] * 100
    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"Чипта: {p_data['title']}",
            description=f"{p_data['title']} ўйинида 1 та чипта",
            payload=f"{p_id}#pay",
            provider_token=PAYMENT_TOKEN,
            currency="UZS",
            prices=[types.LabeledPrice(label="1 та чипта", amount=amount_tiyin)],
            start_parameter="furniture_lottery"
        )
    except Exception as e:
        await callback.message.answer(f"Тўлов тизими созланмоқда: {e}")

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def payment_success_handler(message: types.Message):
    payload = message.successful_payment.invoice_payload
    p_id = payload.split("#")[0]
    p_data = PRODUCTS.get(p_id)
    
    user_ticket = p_data["current_ticket"] if p_data else "—"
    if p_data:
        p_data["current_ticket"] += 1
    title = p_data["title"] if p_data else "Соврин"

    await message.answer(
        f"✅ <b>Тўлов қабул қилинди!</b>\n\n"
        f"🎁 Соврин: <b>{title}</b>\n"
        f"🎟 <b>Сизнинг рақамингиз: #{user_ticket}</b>\n\n"
        f"Омад ёр бўлсин! 🍀",
        parse_mode="HTML"
    )

# Render талаб қиладиган веб-сервер қисми
async def handle_ping(request):
    return web.Response(text="Bot is live and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
