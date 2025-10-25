import logging
from decimal import Decimal, InvalidOperation
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
from database import add_transaction, get_balance, init_db

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе учитывать доходы и расходы.\n\n"
        "Используй команды, например:\n"
        "/income 1000 зарплата — добавить доход\n"
        "/expense 300 продукты — добавить расход\n"
        "/balance — посмотреть баланс"
    )

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_transaction(update, context, "income")

async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_transaction(update, context, "expense")

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE, trans_type: str):
    user_id = update.effective_user.id
    args = context.args

    if len(args) < 1:
        await update.message.reply_text("❌ Укажи сумму и (опционально) категорию.\nПример: /income 5000 зарплата")
        return

    try:
        amount = Decimal(args[0])
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
    except (InvalidOperation, ValueError) as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        return

    category = " ".join(args[1:]) if len(args) > 1 else "без категории"
    add_transaction(user_id, float(amount), category, trans_type)

    action = "доход" if trans_type == "income" else "расход"
    await update.message.reply_text(f"✅ Добавлен {action}: {amount} руб. ({category})")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    income_total, expense_total = get_balance(user_id)
    balance_total = income_total - expense_total

    await update.message.reply_text(
        f"📊 Твой баланс:\n"
        f"Доходы: {income_total:.2f} ₽\n"
        f"Расходы: {expense_total:.2f} ₽\n"
        f"Остаток: {balance_total:.2f} ₽"
    )

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN не найден в .env")

    init_db()

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("income", income))
    app.add_handler(CommandHandler("expense", expense))
    app.add_handler(CommandHandler("balance", balance))

    print("✅ Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()