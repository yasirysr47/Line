import os
import json
from math import floor
from config import post_process_data, cashflow_file, avg_cashflow_file, output_file
from process_record import PreProcess


class Eval():
    def __init__(self):
        self.min_loan = 100
        self.max_loan = 500
        self.repay_time = 2 #month
        self.sub_fee = 5.99
        self.cashflow_map = dict()
        self.avg_cashflow_map = dict()
        if len([name for name in os.listdir(post_process_data) if os.path.isfile("%s/%s"%(post_process_data,name))]) == 0:
            pre_process_obj = PreProcess()
            pre_process_obj.run()
            self.cashflow_map = pre_process_obj.cashflow_map
            self.avg_cashflow_map = pre_process_obj.avg_cashflow_map
        else:
            with open(cashflow_file, "r") as fp:
                self.cashflow_map = json.load(fp)
            with open(avg_cashflow_file, "r") as fp:
                self.avg_cashflow_map = json.load(fp)

        self.eligible_dict = dict()
        self.eligible_amount = 0
        
    def get_score(self, saving, ttl_saving, hm_saving):
        max_score = 100
        score = 0
        if hm_saving - self.sub_fee >= self.min_loan/4:
            score = score + max_score * 0.35
        if hm_saving >= self.min_loan/4:
            score = score + max_score * 0.30
        if saving - self.sub_fee >= self.min_loan/2:
            score = score + max_score * 0.20
        if ttl_saving - self.sub_fee >= self.min_loan:
            score = score + max_score * 0.10
        if ttl_saving - self.sub_fee >= self.min_loan/2:
            score = score + max_score * 0.05

        return score

    def boost_score(self, score, avg_savings, total_savings, basic_expense, subs):
        max_boost = 10
        variable = 5
        ability_to_sub = False
        if avg_savings - self.sub_fee >= self.min_loan/2:
            score += max_boost
            ability_to_sub = True
        if avg_savings - self.sub_fee + variable >= self.min_loan/2:
            score = score + max_boost * 0.6
            ability_to_sub = True
        if avg_savings >= self.min_loan/2:
            score = score + max_boost * 0.3
        if avg_savings + variable >= self.min_loan/2:
            score = score + max_boost * 0.1


        if (total_savings + basic_expense) - self.sub_fee >= self.min_loan/2:
            score += max_boost
            ability_to_sub = True
        if (total_savings + basic_expense) - self.sub_fee + variable >= self.min_loan/2:
            score = score + max_boost * 0.5
            ability_to_sub = True
        if (total_savings + basic_expense) >= self.min_loan/2:
            score = score + max_boost * 0.2
        if (total_savings + basic_expense) + variable >= self.min_loan/2:
            score = score + max_boost * 0.1

        if subs != 0:
            score += max_boost
            ability_to_sub = True
        
        return score, ability_to_sub

    def get_loan_amount(self, score, avg_score):
        avg = (score + avg_score) / 2
        return floor((avg - self.sub_fee)*2)
    
    def boost_eligibility_score(self):
        for key, data in self.avg_cashflow_map.items():
            current_avg_score = self.eligible_dict[key]["avg_return_score"]
            avg_savings = data.get("avg_savings")
            total_savings = data.get("total_savings")
            subscription = data.get("avg_subscription")
            avg_basic_expense = data.get("avg_basic_expense")

            if self.eligible_dict[key]["eligible"]/self.eligible_dict[key]["not_eligible"] > 0.75:
                current_avg_score = current_avg_score + 25
                self.eligible_dict[key]["ability_to_sub"] = True


            new_score, ability_to_sub = self.boost_score(current_avg_score, avg_savings, total_savings, avg_basic_expense, subscription)
            if not self.eligible_dict[key]["ability_to_sub"]:
                self.eligible_dict[key]["ability_to_sub"] = ability_to_sub
            self.eligible_dict[key]["score"] = new_score
            self.eligible_dict[key]["loan_amount"] =  self.get_loan_amount(new_score, current_avg_score)



    def generate_eligible_dict(self):
        eligibility_count_dict = dict()
        ability_to_repay_score = 0
        for key, data in self.cashflow_map.items():
            eligibility_count_dict[key] = dict()
            eligibility_count_dict[key]["eligible"] = 0
            eligibility_count_dict[key]["not_eligible"] = 0
            eligibility_count_dict[key]["avg_return_score"] = 0
            eligibility_count_dict[key]["ability_to_sub"] = False
            return_score = []
            for month, val in data.items():
                saving = val.get("savings")
                total_saving = val.get("total_savings")
                half_month_income = val.get("half_month_income")
                half_month_expense = val.get("half_month_expense")
                half_month_saving = half_month_income + half_month_expense
                ability_to_repay_score = self.get_score(saving, total_saving, half_month_saving)
                eligibility_count_dict[key][month] = ability_to_repay_score
                return_score.append(ability_to_repay_score)
                if ability_to_repay_score > 50:
                    eligibility_count_dict[key]["eligible"] += 1
                else:
                    eligibility_count_dict[key]["not_eligible"] += 1
            avg_score = sum(return_score)/len(return_score)
            eligibility_count_dict[key]["avg_return_score"] = avg_score
            if avg_score > 50:
                eligibility_count_dict[key]["ability_to_sub"] = True
        self.eligible_dict = eligibility_count_dict


    def print_dic(self, ):
        print(self.eligible_dict)

    def write_to_file(self):
        newdict = {user: {key:self.eligible_dict[user][key] for key in ['avg_return_score', 'ability_to_sub', 'score', 'loan_amount']} 
                    for user in self.eligible_dict.keys()}
        with open(output_file, 'w+') as fp:
            json.dump(newdict, fp, indent=4)


    def start_evaluation(self):
        self.generate_eligible_dict()
        self.boost_eligibility_score()
        self.write_to_file()
       
        #self.print_dic()




obj = Eval()
obj.start_evaluation()
#obj.print_dic()
cashflow_map = obj.cashflow_map
avg_cashflow_map = obj.avg_cashflow_map
eligibility_dict = obj.eligible_dict

