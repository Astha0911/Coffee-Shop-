import telebot
from telebot import types
import json
from messages import*
from datetime import datetime

bot = telebot.TeleBot(bot_token)

admin_ids = [---------]

# Load items from JSON file if available
def load_items_from_json():
    try:
        with open("Items/items.json", "r") as json_file:
            loaded_items = json.load(json_file)
            return loaded_items
    except FileNotFoundError:
        return None

def load_weekly_sales():
    try:
        with open("Sales/weekly_sales.json", "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}

def load_monthly_sales():
    try:
        with open("Sales/monthly_sales.json", "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}

def save_weekly_sales(sales_data):
    with open("Sales/weekly_sales.json", "w") as json_file:
        json.dump(sales_data, json_file)

def save_monthly_sales(sales_data):
    with open("Sales/monthly_sales.json", "w") as json_file:
        json.dump(sales_data, json_file)


# Load items from JSON file
loaded_items = load_items_from_json()
items = loaded_items if loaded_items else {}

# Function to load cart for a specific user from JSON file
def load_cart(chat_id):
    cart_file = f"Carts/cart_{chat_id}.json"
    try:
        with open(cart_file, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}

# Function to save cart for a specific user to JSON file
def save_cart(chat_id, cart_data):
    cart_file = f"Carts/cart_{chat_id}.json"
    with open(cart_file, "w") as json_file:
        json.dump(cart_data, json_file)

# Handler for /start command or when user sends any message



# Handler for inline keyboard button callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if call.data == "add":
            pass
        elif call.data == "view":
            view_cart(call.message)
        elif call.data == "remove":
            remove_item_confirm(call.message)
        elif call.data == "edit":
            edit_quantity(call.message)
        elif call.data == "clear":
            clear_cart(call.message,True)
        elif call.data == "done":
            bot.send_message(call.message.chat.id, thankyou_msg)
            compute_total(call.message)
        elif call.data in items.keys():
            category = call.data
            markup = types.InlineKeyboardMarkup(row_width=3)
            for item in items[category]:
                markup.add(types.InlineKeyboardButton(f"{item['name']} ₹{item['price']}",
                                                    callback_data=str(item['id'])))
            bot.send_message(call.message.chat.id, f"Please select an item from {category}:", reply_markup=markup)
        elif call.data.isdigit():
            add_to_cart(call)
        elif call.data.startswith("edit:"):
            select_item_to_edit(call)
        elif call.data.startswith("remove:"):
            select_item_to_remove(call)
        elif call.data in ["weekly_sales", "monthly_sales"]:
            view_sales(call)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"An error occurred: {str(e)}")

def view_sales(call):
    chat_id = call.message.chat.id
    if chat_id not in admin_ids:
        bot.send_message(chat_id, "You are not authorized to view sales data.")
        return

    if call.data == "weekly_sales":
        sales_data = load_weekly_sales()
        sales_type = "Weekly"
    else:
        sales_data = load_monthly_sales()
        sales_type = "Monthly"

    if not sales_data:
        bot.send_message(chat_id, f"No {sales_type.lower()} sales data available.")
        return

    response = f"{sales_type} Sales Data:\n\n"
    for period, amount in sales_data.items():
        response += f"{period}: ₹{amount}\n"
    bot.send_message(chat_id, response)

# Handler for adding item to cart
def add_to_cart(call):
    item_id = int(call.data)
    chat_id = call.message.chat.id
    cart = load_cart(chat_id)
    for category_items in items.values():
        for item in category_items:
            if item['id'] == item_id:
                item_name = item['name']
                if item_name in cart:
                    cart[item_name]['quantity'] += 0
                else:
                    cart[item_name] = {'quantity': 0, "price": item['price']}
                save_cart(chat_id, cart)
                bot.send_message(call.message.chat.id, f"Enter the new quantity for {item_name}:")
                bot.register_next_step_handler(call.message,update_quantity,item_name)

# Function to view cart
def view_cart(message):
    chat_id = message.chat.id
    cart = load_cart(chat_id)
    if len(cart) == 0:
        bot.send_message(chat_id, empty_order, reply_markup=main_menu_markup(chat_id))
    else:
        response = "This is what you have order:\n"
        total_price = 0
        for item_name, data in cart.items():
            response += f"{item_name} (Qty: {data['quantity']}) - ₹{data['price'] * data['quantity']}\n"
            total_price += data['price'] * data['quantity']
        response += f"\nTotal Price: ₹{total_price}"
        bot.send_message(chat_id, response, reply_markup=main_menu_markup(chat_id))

# Function to remove item
def remove_item_confirm(message):
    try:
        chat_id = message.chat.id
        cart = load_cart(chat_id)
        if not cart:
            bot.send_message(chat_id, empty_order, reply_markup=main_menu_markup(chat_id))
            return

        markup = types.InlineKeyboardMarkup(row_width=1)
        for item_name in cart.keys():
            markup.add(types.InlineKeyboardButton(f"Remove {item_name} (Qty: {cart[item_name]['quantity']})", callback_data=f"remove:{item_name}"))
        markup.add(types.InlineKeyboardButton("Cancel", callback_data="cancel"))
        bot.send_message(chat_id, "Select an item to remove from your order:", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {str(e)}")

# Function to handle selecting item to remove
def select_item_to_remove(call):
    chat_id = call.message.chat.id
    item_name = call.data.split(":")[1]
    cart = load_cart(chat_id)
    del cart[item_name]
    save_cart(chat_id, cart)
    bot.send_message(chat_id, f"{item_name} has been removed from your order.", reply_markup=main_menu_markup(chat_id))

# Function to edit quantity of items in cart
def edit_quantity(message):
    try:
        chat_id = message.chat.id
        cart = load_cart(chat_id)
        if not cart:
            bot.send_message(chat_id, empty_order, reply_markup=main_menu_markup(chat_id))
            return

        markup = types.InlineKeyboardMarkup(row_width=1)
        for item_name in cart.keys():
            markup.add(types.InlineKeyboardButton(f"Edit Quantity of {item_name} (Qty: {cart[item_name]['quantity']})", callback_data=f"edit:{item_name}"))
        markup.add(types.InlineKeyboardButton("Cancel", callback_data="cancel"))
        bot.send_message(chat_id, "Select an item to edit its quantity:", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {str(e)}")

# Function to handle selecting item to edit quantity
def select_item_to_edit(call):
    chat_id = call.message.chat.id
    item_name = call.data.split(":")[1]
    bot.send_message(chat_id, f"Enter the new quantity for '{item_name}':")
    bot.register_next_step_handler(call.message, lambda message: update_quantity(message, item_name))

# Function to update quantity
def update_quantity(message, item_name):
    try:
        chat_id = message.chat.id
        new_quantity = int(message.text)
        if new_quantity < 0:
            bot.send_message(chat_id, "Quantity cannot be negative. Please enter a valid quantity.")
            return

        cart = load_cart(chat_id)
        cart[item_name]['quantity'] = new_quantity
        save_cart(chat_id, cart)
        bot.send_message(chat_id, f"<b>{item_name} x{new_quantity}</b> is added into your order .",
                         reply_markup=main_menu_markup(chat_id),parse_mode='HTML')
    except ValueError:
        bot.send_message(chat_id, "Please enter a valid quantity (a non-negative integer).")

# Function to clear cart
def clear_cart(message,s_msg):
    chat_id = message.chat.id
    cart = load_cart(chat_id)
    cart.clear()
    save_cart(chat_id, cart)
    if s_msg:
        bot.send_message(chat_id, "Your order has been cleared.", reply_markup=main_menu_markup(chat_id))

# Function to compute total
def compute_total(message):
    chat_id = message.chat.id
    cart = load_cart(chat_id)
    if len(cart) == 0:
        bot.send_message(chat_id, empty_order, reply_markup=main_menu_markup(chat_id))
    else:
        response = "You have order :\n\n"
        total_price = 0
        for item_name, data in cart.items():
            response += f"{item_name} (Qty: {data['quantity']}) - ₹{data['price'] * data['quantity']}\n"
            total_price += data['price'] * data['quantity']
        response += f"Total Price: ₹{total_price}"
        bot.send_message(message.chat.id,response)
    
    # Record the sale
        now = datetime.now()
        week_key = f"{now.year}-W{now.isocalendar()[1]}"
        month_key = f"{now.year}-{now.month}"

        weekly_sales = load_weekly_sales()
        if week_key not in weekly_sales:
            weekly_sales[week_key] = 0
        weekly_sales[week_key] += total_price
        save_weekly_sales(weekly_sales)

        monthly_sales = load_monthly_sales()
        if month_key not in monthly_sales:
            monthly_sales[month_key] = 0
        monthly_sales[month_key] += total_price
        save_monthly_sales(monthly_sales)

        clear_cart(message,False)

@bot.message_handler(commands=['sales'])
def handle_sales_command(message):
    chat_id = message.chat.id
    if chat_id not in admin_ids:
        bot.send_message(chat_id, "You are not authorized to view sales data.")
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Weekly Sales", callback_data="weekly_sales"),
               types.InlineKeyboardButton("Monthly Sales", callback_data="monthly_sales"))
    bot.send_message(chat_id, "Select the sales data you want to view:", reply_markup=markup)

# Function to handle inline keyboard markup for main menu
def main_menu_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Add Item", callback_data="coffee_shop"),
               types.InlineKeyboardButton("View Order", callback_data="view"),
               types.InlineKeyboardButton("Remove Item", callback_data="remove"),
               types.InlineKeyboardButton("Edit Quantity", callback_data="edit"),
               types.InlineKeyboardButton("Clear Order", callback_data="clear"),
               types.InlineKeyboardButton("Done", callback_data="done"))
    return markup

@bot.message_handler(func=lambda message: True)
def send_welcome(message):
    bot.send_message(message.chat.id,welcome_msg, reply_markup=main_menu_markup(message.chat.id))

# Start polling

bot.polling()
