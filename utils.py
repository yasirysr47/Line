#Excel sheet required column names
COLS = {"sourceCategories" : 0, "transactionType" : 1, "amount" : 2, "date" : 3, "sourceAccountId" : 4}

#transaction id map
transaction_map = {4 : -1, 0 : 0, 1 : 0 , 2 : 1 , 3 : 1 , 5 : 1}



#######
#category classifications
#######
multi_level_list = {"interest", "service", "tax", "transfer"}

#all the essentials category
essentials_list = {"travel", "food and drink", "healthcare", "interest", "payment", "service", "tax"}
child_essential_list = {"automotive", "financial", "food and beverage", "insurance", "rail",\
                         "subscription", "telecommunication services", "utilities", "interest charged", "payment"}

#total obligations
fee_list = {"bank fees"}

#total expense are from these categories
expense_list = essentials_list  | {"community", "recreation", "transfer", "shops"}
child_expense_list = child_essential_list | {"debit", "third party", "withdrawal"}

#total income is calculated based on these categories
income_list = {"transfer", "tax", "interest"}
child_income_list = {"credit", "deposit", "keep the change savings program", "payroll",\
                "third party", "refund", "interest earned"}


def clean_username(filename):
    name = filename #'./data/User4.xlsx'
    new_name = name.rsplit('/', 1)[1]
    return new_name.strip('.xlsx').lower()