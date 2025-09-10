# 1 create a class
# 2 promt the user for their name, coffee type and quantity
# 3 calculate the total
# 4 display it


class CoffeeShop:

    def __init__(self):

        # This is the prices dictionary for the coffee shop's menus'
        self.prices = {
            1: 2.00,
            2: 3.15,
            3: 4.00,
            4: 4.99
        }

        # This is the coffee types
        self.coffee_types = {
            1: 'black coffee',
            2: 'espresso',
            3: 'latte',
            4: 'cappuccino'
        }
        # this is the receipt we'll print out at the end.
        self.reciept = {
            'name': '',
            'type': '',
            'total': ''
        }
        # this funciton will prompt the user for their name, choice, coffee type
        self._promptUser()

    def _promptUser(self):

        print("Hello, welcome to our coffee shop,what is your name?")

        """
        This while loop will check if the name entered by 
        the user is string, otherwise the program will repeat
        the prompt until the user enters a valid string.
        """
        while True:
            try:
                name = input("name: ")
                if name.isalpha():
                    # The "break" statement will exit the entire loop once the
                    # user enters the correct string.
                    break
                else:
                    print("Error: enter a valid string name")
            except ValueError:
                print("An error occured.")

        # We update the receipt dict's name
        self.reciept['name'] = name

        menu = """Our Menu
                1) Black Coffee
                2) Espresso
                3) Latte
                4) Cappuccino
                """
        print(menu)

        """
        This while loop prompts the user for the choice 
        of coffee they want to buy from the menu. And the 
        loop checks if the choice entered by the user is 
        between 1-4, but not lower or higher.
        
        """
        while True:
            try:
                choice = int(input("choice: "))
                if choice >= 1 and choice <= 4:
                    break
                else:
                    print("Error: not a valid choice: try again.")
            except ValueError:
                print("An error occured.")

        while True:
            try:
                quantity = int(input("quantity: "))

                if quantity >= 1 and isinstance(quantity, int):
                    break
                else:
                    print("Error: not a valid quantity.")
            except ValueError:
                print("Error: an error occured.")

        # We calll the calcTotal function to calculate the total
        self._calcTotal(choice, quantity)

    def _calcTotal(self, choice, quantity):
        # We check if the choice made by the user is between 1-4
        if choice in self.prices:
            # and if the choice is between 1-4
            # we get the price associated with the choice they
            # made using the price dictionary
            price = self.prices[choice]
            # and we get the coffee type as well, by getting the type from coffee_type dict
            coffeeType = self.coffee_types[choice]
            # we calculate the total by multiplying the price and the
            # quantity.
            total = price * quantity
            """
            We update the receipt dict's type and total keys.
            we set type to coffeeType, and total to total.
            Although unneccessery, I rounded the total. 
            """
            self.reciept['type'] = coffeeType
            self.reciept['total'] = round(total, 2)
            # we return the recieppt here
            return self.reciept
        else:
            print("An error occured calculating the receipt.")

    def getReceipt(self):
        print("\nHere's your receipt, thank you for shopping with us.")
        print()
        # printing the receipt dict, by getting the keys and values of
        # the dict and printing it in a formated way using the f string.
        for key, val in self.reciept.items():
            print(f'{key}\t{val}')
        print("---------------------------------------")

# created an instance of the class we made CoffeeShop
cs = CoffeeShop()
# called the getReceipt() function to display
cs.getReceipt()

