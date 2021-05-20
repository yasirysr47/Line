import time
from utils import clean_username
from config import user_data_files
from evaluate import avg_cashflow_map, eligibility_dict

def screen():
    print("==="*20)
    print("available users in the database are:")
    for user in user_data_files:
        print(clean_username(user))
    print("---"*5)
    print("available functionalities are :")
    s = """
    1. get users average monthly INCOME\n
    2. get users average monthly EXPENSE\n
    3. get users average monthly Essential Expense\n
    4. get users average monthly FEES\n
    5. loan amount eligible\n
    6. users ability to pay back within 2 months\n
    7. users ability to pay the subscription fees\n
    """
    print(s)
    print("==="*20)
    print("enter your input in the following way for the result")
    print("<USER NAME> <FUNCTION NUMBER>\ntype exit to stop")
    print("---"*20)

def run():
    func_map = {
        1: "avg_income",
        2: "avg_expense",
        3: "avg_basic_expense",
        4: "avg_bank_fee",
        5: "loan_amount",
        6: "avg_return_score",
        7: "ability_to_sub"
    }
    while(1):
        screen()
        inp = input("=>  ")
        inp = inp.lower()
        if inp == "exit":
            print("Thanks")
            break
        user, func = inp.split(" ")
        func = int(func)
        elg_dic = eligibility_dict.get(user)
        avg_dic = avg_cashflow_map.get(user)
        x = func_map.get(func)
        if func == 7:
            if elg_dic.get(x):
                print("{} is eligible for a monthly subscription.".format(user))
            else:
                print("{} is not eligible for a monthly subscription.".format(user))
        elif func == 6:    
            print("{} can pay the amount back in 2 months. (confidence = {:.2f}%)".format(user, elg_dic.get(x)))
        elif func == 5:    
            print("{} is eligible for ${:.2f}".format(user, elg_dic.get(x)))
        elif func == 4:    
            print("{} average fees paid in a month is ${:.2f}".format(user, avg_dic.get(x)))
        elif func == 3:    
            print("{} average eessential expense in a month is ${:.2f}".format(user, avg_dic.get(x)))
        elif func == 2:    
            print("{} average expense in a month is ${:.2f}".format(user, avg_dic.get(x)))
        elif func == 1:    
            print("{} average income in a month is ${:.2f}".format(user, avg_dic.get(x)))
        else:
            print("INVALID FUNCTION")
        time.sleep(5)


run()


    
