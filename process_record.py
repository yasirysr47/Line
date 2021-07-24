import os
import xlrd
import utils
import json
import pandas as pd
from utils import *
from utils import clean_username
from config import user_data_files, cashflow_file, avg_cashflow_file, bank_details_filename
from datetime import datetime


class PreProcess():
    def __init__(self):
        self.primary_bank_dict = dict()
        '''
        "user1": {
            "08-2018" : {
                half_month_expense: 0,
                half_month_income: 0,
                income: 0,
                expense: 0,
                savings: 0,
                subscription: (amount, count),
                bank_fee: 0,
                basic_expense: 0,
            },
            "09-2018" :{
                .......
            },
        },
        "user2" :{
            ....
        }
        '''
        self.cashflow_map = dict()
        '''
        "user1": {
            avg_expense: 0,
            avg_income: 0,
            avg_savings: 0,
            total_subscription: (amount, count),
            avg_bank_fee: 0,
            avg_basic_expense: 0,
            primanry_bank: [ :top 40%]
        },
        "user2" :{
            ....
        }
        '''
        self.avg_cashflow = dict()
    
    def init_vars(self):
        self.avg_half_monthly_income = 0
        self.avg_half_monthly_expense = 0
        self.avg_half_monthly_savings = 0
        self.avg_half_monthly_debt = 0

        self.avg_monthly_income = 0
        self.avg_monthly_expense = 0
        self.avg_monthly_basic_expense = 0
        self.avg_monthly_savings = 0

        self.avg_monthly_debt = 0

        self.monthly_subscriptions = []
        self.avg_monthly_subscription_amount = 0

        self.avg_monthly_bank_fee = 0
        self.primary_bank = dict()

        self.total_savings = []

        self.half_month_income_list = []
        self.monthly_income_list = []

        self.half_month_expense_list = []
        self.monthly_expense_list = []

        self.monthly_basic_expense_list = []

        self.monthly_debt = []

        self.monthly_bank_fee = []

    def print_list(self):
        print("monthly_subscriptions -> {}".format(self.monthly_subscriptions))
        print("half_month_income_list -> {}".format(self.half_month_income_list))
        print("monthly_income_list -> {}".format(self.monthly_income_list))
        print("half_month_expense_list -> {}".format(self.half_month_expense_list))
        print("monthly_expense_list -> {}".format(self.monthly_expense_list))
        print("monthly_basic_expense_list -> {}".format(self.monthly_basic_expense_list))
        print("monthly_debt -> {}".format(self.monthly_debt))
        print("monthly_bank_fee -> {}".format(self.monthly_bank_fee))
        print("------"*10)

    def print_dicts(self):
        print("avg_cashflow -> {}".format(self.avg_cashflow))
        print("cashflow_map -> {}".format(self.cashflow_map))
        print("primary_bank_dict -> {}".format(self.primary_bank_dict))
        print("------"*10)


    def clean_date(self, date):
        new_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        return new_date.date()

    def track_bank(self, id, boost=1):
        if self.primary_bank.get(id):
            self.primary_bank[id] += boost
        else:
            self.primary_bank[id] = boost

    def get_bank_details(self):
        top_bank_pick =  int(len(self.primary_bank) * 0.4) if len(self.primary_bank) > 4 else 1
        primary_bank = sorted(self.primary_bank.items(), key=lambda kv: kv[1], reverse=True)[:top_bank_pick]
        key = clean_username(self.filename)
        self.primary_bank_dict[key] = primary_bank
        self.avg_cashflow[key]["primary_bank"] = [bank[0] for bank in primary_bank]

    def make_avg_cashflow(self):
        self.avg_half_monthly_income = sum(self.half_month_income_list)/len(self.half_month_income_list)
        self.avg_half_monthly_expense = sum(self.half_month_expense_list)/len(self.half_month_expense_list)
        self.avg_half_monthly_savings = self.avg_half_monthly_income + self.avg_half_monthly_expense

        self.avg_monthly_income = sum(self.monthly_income_list)/len(self.monthly_income_list)
        self.avg_monthly_expense = sum(self.monthly_expense_list)/len(self.monthly_expense_list)
        self.avg_monthly_basic_expense = sum(self.monthly_basic_expense_list)/len(self.monthly_basic_expense_list)
        self.avg_monthly_savings =  self.avg_monthly_income + self.avg_monthly_expense

        self.avg_monthly_subscription_amount = sum(self.monthly_subscriptions)/len(self.monthly_subscriptions)

        self.avg_monthly_bank_fee = sum(self.monthly_bank_fee)/len(self.monthly_bank_fee)
        total_savings = sum(self.total_savings)
        
        tmp_dict = dict()
        
        
        tmp_dict = {
            "avg_expense": self.avg_monthly_expense,
            "avg_income": self.avg_monthly_income,
            "avg_savings": self.avg_monthly_savings,
            "total_savings": total_savings,
            "avg_subscription": self.avg_monthly_subscription_amount,
            "avg_bank_fee": self.avg_monthly_bank_fee,
            "avg_basic_expense": self.avg_monthly_basic_expense,
            "primary_bank": []
        }
        key = clean_username(self.filename)
        self.avg_cashflow[key] = tmp_dict
        
        


    def process_for_monthly_data(self, month, year):
        
        key = clean_username(self.filename)
        user_key = "%s"%key
        key_date = "{}-{}".format(month, year)
        tmp_dict = dict()

        half_month_income = self.half_month_income_list[-1]
        half_month_expense = self.half_month_expense_list[-1]
        income = self.monthly_income_list[-1]
        expense = self.monthly_expense_list[-1]
        savings = income + expense
        self.total_savings.append(savings)
        total_savings = sum(self.total_savings)
        subscription = self.monthly_subscriptions[-1]
        bank_fee = self.monthly_bank_fee[-1]
        basic_expense = self.monthly_basic_expense_list[-1]
        
        tmp_dict[key_date] = {
            "half_month_income": half_month_income,
            "half_month_expense": half_month_expense,
            "income": income,
            "expense": expense,
            "savings": savings,
            "total_savings": total_savings,
            "subscription": subscription, 
            "bank_fee": bank_fee,
            "basic_expense": basic_expense,
        }

        if user_key not in self.cashflow_map:
            self.cashflow_map[user_key] = dict()
        self.cashflow_map[user_key][key_date] = tmp_dict[key_date]
            


    def process(self, excel_data):
        start_date = 1
        cur_year = 0
        prev_year = 0
        cur_month = 0
        prev_month = 0

        monthly_expense = 0
        half_month_expense = 0
        basic_expense = 0

        monthly_income = 0
        half_month_income = 0

        bank_fee = 0
        subscription = 0
        debt = 0        
        half_flag = 0


        for i, row in excel_data.iterrows():
            category_list = json.loads(row[COLS.get("sourceCategories")])
            transaction_type = json.loads(row[COLS.get("transactionType")])
            amount = json.loads(row[COLS.get("amount")])
            date = row[COLS.get("date")].date()
            bank_id = row[COLS.get("sourceAccountId")]
            trans_flag = transaction_map.get(transaction_type, 0)
            parent, child = None, None
            if len(category_list) == 2:
                parent, child = category_list
            elif len(category_list) > 2:
                parent, child, _ = category_list
            elif len(category_list) == 1:
                parent = category_list[0]

            cur_year = date.year
            cur_month = date.month

            if prev_month and prev_month != cur_month:
                self.half_month_expense_list.append(half_month_expense)
                self.monthly_expense_list.append(monthly_expense)
                self.monthly_basic_expense_list.append(basic_expense)
                self.half_month_income_list.append(half_month_income)
                self.monthly_income_list.append(monthly_income)
                self.monthly_bank_fee.append(bank_fee)
                self.monthly_subscriptions.append(subscription)
                self.monthly_debt.append(debt)

                self.process_for_monthly_data(prev_month, prev_year)

                start_date = 1
                cur_month = 0
                prev_month = 0

                monthly_expense = 0
                half_month_expense = 0
                basic_expense = 0

                monthly_income = 0
                half_month_income = 0

                bank_fee = 0
                subscription = 0
                debt = 0  

                half_flag = 0
            

            if date.day - start_date <= 15:
                half_flag = 1
            else:
                half_flag = 0

            if trans_flag == 1:
                #definetly its income
                if parent in income_list and child in child_income_list:
                    if child in ["payroll"] or (parent in ["tax"] and child in ["refund"]):
                        self.track_bank(bank_id,boost=10)
                    else:
                        self.track_bank(bank_id, boost=5)
                else:
                    self.track_bank(bank_id, boost=2)
                
                monthly_income += amount
                if half_flag:
                    half_month_income += amount

            elif trans_flag == -1:
                #definetly  expense
                self.track_bank(bank_id)
                monthly_expense += amount
                if half_flag:
                    half_month_expense += amount
            else:
                #can be income or expense
                self.track_bank(bank_id)
                if parent in fee_list:
                    monthly_expense += amount
                    bank_fee += amount
                elif parent in multi_level_list:
                    if (child and child in child_expense_list) or amount < 0:
                        if child in child_essential_list:
                            basic_expense += amount
                            if child == "subscription":
                                subscription += amount
                        if half_flag:
                            half_month_expense += amount
                        monthly_expense += amount
                    elif (child and child in child_income_list) or amount > 0:
                        if half_flag:
                            half_month_income += amount
                        monthly_income += amount
                elif parent in expense_list:
                    if child and child in child_expense_list:
                        if child in child_essential_list:
                            basic_expense += amount
                    elif parent in essentials_list:
                        basic_expense += amount
                    if half_flag:
                        half_month_expense += amount
                    monthly_expense += amount
                else:
                    if amount > 0:
                        if half_flag:
                            half_month_income += amount
                        monthly_income += amount
                    else:
                        if half_flag:
                            half_month_expense += amount
                    monthly_expense += amount
            
            prev_month = cur_month
            prev_year = cur_year
        
        self.half_month_expense_list.append(half_month_expense)
        self.monthly_expense_list.append(monthly_expense)
        self.monthly_basic_expense_list.append(basic_expense)
        self.half_month_income_list.append(half_month_income)
        self.monthly_income_list.append(monthly_income)
        self.monthly_bank_fee.append(bank_fee)
        self.monthly_subscriptions.append(subscription)
        self.monthly_debt.append(debt)
        
        self.process_for_monthly_data(prev_month, prev_year)

    def post_process(self):
        '''
        '''
        if not os.path.exists('post_process_data'):
            os.makedirs('post_process_data')
        cash_flow_file = cashflow_file
        avg_cash_flow_file = avg_cashflow_file
        bank_details_file = bank_details_filename
        process_file = [(self.cashflow_map, cash_flow_file),
                        (self.avg_cashflow, avg_cash_flow_file),
                        (self.primary_bank_dict, bank_details_file)]
        for dic, files in process_file:
            with open(files, "w+") as fp: 
                json.dump(dic, fp, indent=4)



    def preprocess_and_bucket_data(self, filename):
        df = pd.read_excel(filename)
        data = pd.DataFrame(df, columns=COLS.keys())
        data = data.apply(lambda x: x.astype(str).str.lower())
        data['date'] = pd.to_datetime(data.date)
        excel_data = data.sort_values(by='date')
        self.init_vars()
        self.filename = filename
        self.process(excel_data)
        #self.print_list()
        self.make_avg_cashflow()
        self.get_bank_details()
        self.post_process()
        #self.print_dicts()
        

    def start_preprocess(self):
        for each in user_data_files:
            self.preprocess_and_bucket_data(each)


    def run(self):
        obj = PreProcess()
        obj.start_preprocess()



        


PreProcess().run()
        


