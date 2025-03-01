import os
import clips
import psycopg2
import io
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, CallbackContext

# Load environment variables
load_dotenv()

# Read values from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT
)
cursor = conn.cursor()

# Load CLIPS
env = clips.Environment()
env.load("refund.clp")

# Function to fetch order details
def get_order_details(order_id):
    cursor.execute("SELECT id, customer, status, payment, return_period, amount FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    
    if order:
        return f"(order (id {order[0]}) (customer {order[1]}) (status {order[2]}) (payment {order[3]}) (return_period {order[4]}) (amount {order[5]}))"
    return None

# Process refund logic
def process_refund(order_id):
    order_fact_string = get_order_details(order_id)

    print("order_fact:", order_fact_string)
    if order_fact_string:
        env.reset()
        env.assert_string(order_fact_string)

        # output = []
        # # def clips_output(text):
        # #     output.append(text)

        # # env.add_router("stdout", clips_output)
        # env.add_router("stdout", lambda text: output.append(text))
        # env.run()
        
        # return "\n".join(output) if output else "No refund rules matched."
        
        # Capture stdout
        # old_stdout = sys.stdout
        # redirected_output = sys.stdout = io.StringIO()

        # env.run()

        # sys.stdout = old_stdout #reset stdout

        # output = redirected_output.getvalue().strip()
        # print("output from clips:", output)
        # redirected_output.close()

        # return output if output else "No refund rules matched."
        captured_output = []

        def clips_output_handler(value):
            captured_output.append(str(value))

        env.define_function(clips_output_handler, "python-output")

        env.reset()
        env.assert_string(order_fact_string)
        # env.eval('(printout python-output "start of output" crlf)') #example of how to print to the python function.
        env.run()
        env.undefine_function("python-output") #remove the function.
        # env.eval('(printout python-output "end of output" crlf)') #example of how to print to the python function.
        print("captured_output:", captured_output)
        return "".join(captured_output)    
    return "❌ Order not found. Try again."

# Handle refund request
async def handle_message(update: Update, context: CallbackContext) -> None:
    order_id = update.message.text.strip()

    if order_id.isdigit():
        refund_info = process_refund(order_id)
        
        if "FULL refund" in refund_info or "PARTIAL refund" in refund_info:
            cursor.execute("INSERT INTO refund_requests (order_id) VALUES (%s) ON CONFLICT (order_id) DO NOTHING", (order_id,))
            conn.commit()

            keyboard = [
                [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{order_id}"),
                 InlineKeyboardButton("❌ Reject", callback_data=f"reject_{order_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(refund_info, reply_markup=reply_markup)
        else:
            await update.message.reply_text(refund_info)
    else:
        await update.message.reply_text("❌ Please enter a valid numeric Order ID.")

# Approve or reject refunds
async def refund_decision(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    action, order_id = query.data.split("_")

    if action == "approve":
        status = "approved"
    elif action == "reject":
        status = "rejected"
    
    cursor.execute("UPDATE refund_requests SET status = %s, approved_by = %s WHERE order_id = %s",
                   (status, query.from_user.username, order_id))
    conn.commit()

    await query.edit_message_text(text=f"🔹 Refund for Order {order_id} has been **{status.upper()}**.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍️ Welcome to the Refund Bot!\nSend an order ID to check refund eligibility.")

# Main function
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Fixed Filters issue
    app.add_handler(CallbackQueryHandler(refund_decision))

    app.run_polling()  # Fixed polling issue

if __name__ == "__main__":
    main()
