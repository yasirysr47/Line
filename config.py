import os
post_process_data = "./post_process_data"
cashflow_file = "./post_process_data/cash_flow.json"
avg_cashflow_file = "./post_process_data/avg_cash_flow.json"
bank_details_filename = "./post_process_data/bank_details.json"
output_file = "./post_process_data/pred.json"
user_data_dir = "./data"
user_data_files = []

for filename in os.listdir(user_data_dir):
    files = filename.lower()
    if files.startswith('user') and files.endswith('xlsx'):
        user_data_files.append("{}/{}".format(user_data_dir,filename))

