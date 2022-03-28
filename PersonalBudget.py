import csv
import pandas as pd
import matplotlib.pyplot as plt


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)


def home():
    print("Hello! Which calculator would you like to use?\n1. American Express")
    while True:
        answer = input(">")
        if answer == "1":
            amex()
            return
        # elif answer == "2":
        #     wells_fargo()
        #     return
        else:
            print(num_error())


def amex():  # uses American Express CSV
    path = input("Please enter the file path: ")  # csv file downloaded from website - sorry will not provide mine :)
    df = pd.read_csv(path, delimiter=",",
                     parse_dates=True, skipinitialspace=True)

    df = df.loc[df["Description"] != "AUTOPAY PAYMENT - THANK YOU"]
    df = df.iloc[::-1].reset_index(drop=True)  # reverse the df
    df["Description"] = df.Description.str.split().str[:].apply(lambda x: " ".join(x))  # goodbye whitespace
    print(df)
    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]
    all_total = round(df["Amount"].sum(), 2)
    statement_date = f"{start_date} - {end_date}"
    print(f"AMEX STATEMENT DATE: {statement_date} ")
    print(f"OVERALL TOTAL: {all_total}")
    input("\nPress enter to initiate manual categorizing.")
    categories = {"food": 0, "gas": 0, "life": 0, "pets": 0}  # default categories

    for index, row in df.iterrows():

        print(categories)
        date = row["Date"]
        amount = str(row["Amount"])
        card_member = row["Card Member"]
        description = row["Description"]
        account_num = row["Account #"]
        while True:
            print(f"\nDate: {date}"  # printed format of each transaction
                  f"\nDescription: {description}"
                  f"\nCard Holder: {card_member}"
                  f"\nAmount: {amount}")
            print("Which category does this belong to?")
            cat_join = ""
            for k, v in categories.items():
                cat_join += f"[{k}] "  # joining categories into one line
            print(f"Valid categories: {cat_join}")  # shows active categories for ease of use
            answer = input(">").lower()
            if answer.split(" ")[0] == "!addcat":  # adds new category with 0 value
                add_category(answer, categories)
                continue
            elif answer.split(" ")[0] == "!return":  # if transaction is a money back return
                categories[answer.split(" ")[1]] = round(float(categories[answer.split(" ")[1]]) +
                                                         float(amount), 2)
                break
            elif answer.split(" ")[0] == "!split":  # splits specified amount into specified category
                try:
                    split = float(answer.split()[1])  # answer is passed to fx not split
                except ValueError:
                    print("ERROR: Unexpected format. Expected format for this command: !split amount category")
                    input("Press enter to acknowledge.")
                    continue
                if split > float(amount):
                    print("ERROR: Split amount entered exceeds original amount.")
                    input("Press enter to acknowledge.")
                    continue
                else:
                    try:
                        amount = split_transaction(answer, amount, categories)  # returns remaining amount
                        continue
                        # TODO split errors and other command errors
                    except IndexError:
                        print("ERROR. Unexpected format. Expected format for this command: !split amount category")
                        input("Press enter to acknowledge.")
                        continue
                    except KeyError:
                        print("ERROR. Invalid category.")
                        input("Press enter to acknowledge.")
                        continue
            elif answer == "!totals":  # prints current category totals
                totals(categories)
                continue
            elif answer == "!help":  # prints list of commands and what they do
                help_command()
                continue
            else:
                success = update_category_value(answer, categories, amount)  # returns True or False
                if success is True:  # next transaction
                    break
                if success is False:  # try again
                    continue
    print("\nEnd of statement. Fetching category totals..\n")  # end of iteration
    for k, v in categories.items():  # print category totals
        two_d_v = "{:.2f}".format(v)
        print(f"{k.title()}: {two_d_v}")
    input("\nPress enter to return to home screen.")
    home()
    return


# def wells_fargo():  # Uses Wells Fargo CSV
#     path = input("Please enter the file path: ")  # csv file downloaded from website - sorry will not provide mine :)
#     df = pd.read_csv(path, delimiter=",",
#                      parse_dates=True, header=None,
#                      names=["Date", "Amount", "?", "Check Number", "Description"])
#
#     df = df.iloc[::-1].reset_index(drop=True)  # reverse the df
#     df.loc[df["Amount"] >= 0, "Transaction Type"] = "Deposit"
#     df.loc[df["Amount"] < 0, "Transaction Type"] = "Withdrawal"
#     df.loc[df["Amount"] < 0, "Amount"] = df["Amount"] * -1  # flip negatives after using them to define transaction
#     print(df)
#     start_date = df["Date"].iloc[0]
#     end_date = df["Date"].iloc[-1]
#     all_total = df["Amount"].sum()
#     statement_date = f"{start_date} - {end_date}"
#     print(f"WELLS FARGO STATEMENT DATE: {statement_date} ")
#     print(f"OVERALL TOTAL: {all_total}")
#     input("\nPress enter to initiate manual categorizing.")
#     categories = {"amex": 0, "transfer": 0, "bills": 0}
#     for index, row in df.iterrows():
#         while True:
#             print(categories)
#             date = row["Date"]
#             amount = str(row["Amount"])
#             not_sure = row["?"]
#             check_number = row["Check Number"]
#             description = row["Description"]
#             transaction_type = row["Transaction Type"]
#
#             if transaction_type == "Deposit":
#                 break
#             print(f"\nDate: {date}\nDescription: {description}\nAmount: {amount}")
#             print("Which category does this belong to?")
#             cat_join = ""
#             for k, v in categories.items():
#                 cat_join += f"[{k}] "
#             print(f"Valid categories: {cat_join}")
#             answer = input(">").lower()
#             if answer.split(" ")[0] == "!addcat":
#                 new_category = answer[8:]
#                 categories[new_category] = 0
#                 print(f"Category [{new_category}] added.")
#                 input("\nPress enter to continue.")
#                 continue
#             elif answer == "!help":
#                 help_command()
#                 input("\nPress enter to continue.")
#                 continue
#             elif answer == "!totals":
#                 totals(categories)
#                 continue
#             elif answer.split(" ")[0] == "!return":
#                 categories[answer.split(" ")[1]] = round(float(categories[answer.split(" ")[1]]) + float(amount), 2)
#                 break
#             else:
#                 try:
#                     categories[answer] = round(float(categories[answer]) + float(amount), 2)
#                     break
#                 except KeyError:
#                     print("Invalid command. Please enter a valid category or type !help.")
#             print("\nEnd of statement. Fetching category totals..\n")
#             for k, v in categories.items():
#                 two_d_v = "{:.2f}".format(v)
#                 print(f"{k.title()}: {two_d_v}")
#     print(categories)
#     fig = plt.figure(figsize=(7, 7))
#     ax = plt.subplot(111)
#     ax.pie(list(categories.values()), labels=list(categories.keys()))
#     ax.axis("equal")
#     plt.show()
#     input("Press enter to return to home screen.")
#     home()
#     return



# def wells_fargo():  # Uses Wells Fargo CSV
#     path = input("Please enter the file path: ")  # csv file downloaded from website - sorry will not provide mine :)
#     with open(path, mode="r") as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=",")
#         all_total = 0
#         statement_date = ""
#         for line in enumerate(csv_reader):
#             date = line[1][0]
#             amount = line[1][1].rstrip()
#             not_sure = line[1][2]
#             check_number = line[1][3]
#             description = line[1][4].rstrip()
#             if line[0] == 1:
#                 statement_date += str(date)
#             all_total = round(all_total + float(amount), 2)
#         statement_date = f"{date} - {statement_date}"
#         print(f"WELLS FARGO STATEMENT DATE: {statement_date} ")
#         print(f"OVERALL TOTAL: {all_total}")
#     input("\nPress enter to initiate manual categorizing.")
#     with open(path, mode="r") as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=",")
#         copy_statement = []
#         categories = {"amex": 0, "transfer": 0, "bills": 0, "income": 0}
#         for line in enumerate(csv_reader):
#             copy_statement.append(line)
#         for line in reversed(copy_statement):
#             date = line[1][0]
#             amount = line[1][1].rstrip()
#             not_sure = line[1][2]
#             check_number = line[1][3]
#             description = line[1][4].rstrip()
#             while True:
#                 if amount.startswith("-"):
#                     print(f"\nDate: {date}\nDescription: {description}\nWITHDRAWAL Amount: {amount}")
#                 else:
#                     print(f"\nDate: {date}\nDescription: {description}\nDEPOSIT Amount: {amount}")
#                 print("Which category does this belong to?")
#                 cat_join = ""
#                 for k, v in categories.items():
#                     cat_join += f"[{k}] "
#                 print(f"Valid categories: {cat_join}")
#                 answer = input(">").lower()
#                 if answer.split(" ")[0] == "!addcat":
#                     new_category = answer[8:]
#                     categories[new_category] = 0
#                     print(f"Category [{new_category}] added.")
#                     input("\nPress enter to continue.")
#                     continue
#                 elif answer == "!help":
#                     help_command()
#                     input("\nPress enter to continue.")
#                     continue
#                 elif answer == "!totals":
#                     totals(categories)
#                     continue
#                 elif answer.split(" ")[0] == "!return":
#                     categories[answer.split(" ")[1]] = round(float(categories[answer.split(" ")[1]]) + float(amount), 2)
#                     break
#                 else:
#                     try:
#                         categories[answer] = round(float(categories[answer]) + float(amount), 2)
#                         break
#                     except KeyError:
#                         print("Invalid command. Please enter a valid category or type !help.")
#         print("\nEnd of statement. Fetching category totals..\n")
#         for k, v in categories.items():
#             two_d_v = "{:.2f}".format(v)
#             print(f"{k.title()}: {two_d_v}")
#     input("Press enter to return to home screen.")
#     home()
#     return


    # AMEX BACK UP
    # path = input("Please enter the file path: ")  # csv file downloaded from website - sorry will not provide mine :)
    # with open(path, mode="r") as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=",")
    #     all_total = 0  # for header use
    #     statement_date = ""  # header string
    #     for line in enumerate(csv_reader):  # run through whole file to find statement sum and date range
    #         if line[0] == 0:  # first line of file is noise
    #             continue
    #         date = line[1][0]
    #         description = line[1][1][:20].upper().rstrip()
    #         card_member = line[1][2]
    #         account = line[1][3]
    #         amount = line[1][4].rstrip()
    #         if line[0] == 1:
    #             statement_date += str(date)  # date of first line encountered
    #         all_total = round(all_total + float(amount), 2)  # calculate total of all transactions
    #     statement_date = f"{date} - {statement_date}"  # format header for date range of statement
    #     print(f"AMEX STATEMENT DATE: {statement_date} ")
    #     print(f"OVERALL TOTAL: {all_total}")
    # print("\nWhat would you like to do?\n1. Manually categorize\n2. Calculate sum of identical descriptions")
    # while True:
    #     answer = input(">")
    #     if answer == "1":  # manually categorize
    #         with open(path, mode="r") as csv_file:
    #             csv_reader = csv.reader(csv_file, delimiter=",")
    #             copy_statement = []
    #             categories = {"food": 0, "gas": 0, "life": 0, "pets": 0}  # default categories
    #             for line in enumerate(csv_reader):
    #                 if line[0] == 0:  # line 0 is noise
    #                     continue
    #                 copy_statement.append(line)  # create a list copy so it can be reversed
    #             for line in reversed(copy_statement):  # reversed for iterating chronological dates instead of default
    #                 date = line[1][0]
    #                 description = line[1][1][:20].upper().rstrip()
    #                 card_holder = line[1][2]
    #                 account_number = line[1][3]
    #                 amount = line[1][4].rstrip()
    #                 while True:
    #                     print(f"\nDate: {date}"  # printed format of each transaction
    #                           f"\nDescription: {description}"
    #                           f"\nCard Holder: {card_holder}"
    #                           f"\nAmount: {amount}")
    #                     print("Which category does this belong to?")
    #                     cat_join = ""
    #                     for k, v in categories.items():
    #                         cat_join += f"[{k}] "  # joining categories into one line
    #                     print(f"Valid categories: {cat_join}")  # shows active categories for ease of use
    #                     answer = input(">").lower()
    #                     if answer.split(" ")[0] == "!addcat":  # adds new category with 0 value
    #                         add_category(answer, categories)
    #                         continue
    #                     elif answer.split(" ")[0] == "!return":  # if transaction is a money back return
    #                         categories[answer.split(" ")[1]] = round(float(categories[answer.split(" ")[1]]) +
    #                                                                  float(amount), 2)
    #                         break
    #                     elif answer.split(" ")[0] == "!split":  # splits specified amount into specified category
    #                         amount = split_transaction(answer, amount, categories)  # returns remaining amount
    #                         continue
    #                     elif answer == "!totals":  # prints current category totals
    #                         totals(categories)
    #                         continue
    #                     elif answer == "!help":  # prints list of commands and what they do
    #                         help_command()
    #                         continue
    #                     else:
    #                         success = update_category_value(answer, categories, amount)  # returns True or False
    #                         if success is True:  # next transaction
    #                             break
    #                         if success is False:  # try again
    #                             continue
    #             print("\nEnd of statement. Fetching category totals..\n")  # end of iteration
    #             for k, v in categories.items():  # print category totals
    #                 two_d_v = "{:.2f}".format(v)
    #                 print(f"{k.title()}: {two_d_v}")
    #         break
    #     if answer == "2":  # calculate sum of identical descriptions
    #         with open(path, mode="r") as csv_file:
    #             csv_reader = csv.reader(csv_file, delimiter=",")
    #             shop_totals = {}
    #             for line in enumerate(csv_reader):
    #                 print(line)
    #                 if line[0] == 0:
    #                     continue
    #                 date = line[1][0]
    #                 description = line[1][1][:20].upper().rstrip()
    #                 card_member = line[1][2]
    #                 account = line[1][3]
    #                 amount = line[1][4].rstrip()
    #                 if description not in shop_totals:  # combines like descriptions' values
    #                     shop_totals[description] = amount
    #                 elif description in shop_totals:
    #                     shop_totals[description] = round(float(shop_totals[description]) + float(amount), 2)
    #             for k, v in shop_totals.items():  # print descriptions and values
    #                 two_d_v = "{:.2f}".format(float(v))
    #                 print(k.ljust(22) + str(two_d_v).rjust(1))
    #         break
    #     else:
    #         print(num_error())
    # home()
    # return


def update_category_value(answer, categories, amount):
    try:  # amount + category value
        categories[answer] = round(float(categories[answer]) + float(amount), 2)
        return True  # True if input works
    except KeyError:
        print("INVALID COMMAND. Please enter a valid category or type !help.")
        input("Press enter to try again.")
        return False  # False if input is incorrect


def add_category(answer, categories):
    new_category = answer.split(" ")[1]
    categories[new_category] = 0
    print(f"Category [{new_category}] added.")
    input("\nPress enter to continue.")
    return


def split_transaction(answer, amount, categories):
    print(len(str(answer).split()[1].split(".")[1]))
    if len(str(answer).split()[1].split(".")[1]) > 2:
        print("ERROR. Too many decimal places entered.")
        input("Press enter to acknowledge.")
        return amount
    split_amount = answer.split(" ")[1]
    split_category = answer.split(" ")[2]
    amount = round(float(amount) - float(split_amount), 2)
    categories[split_category] = round(float(categories[split_category]) +
                                       float(split_amount), 2)
    print(f"{split_amount} has gone into category [{split_category}]. ")
    input("Press enter to loop back to the transaction with an updated remaining amount.")
    return amount


def totals(categories):
    print()
    for k, v in categories.items():
        two_d_v = "{:.2f}".format(v)
        print(f"{k.title()}: {two_d_v}")
    input("\nPress enter to get back to transactions.")
    return


def help_command():
    print("\nCommands:\n"
          "!addcat category       -- adds a new category that you name\n"
          "!totals                -- shows current totals for each category\n"
          "!return category       -- denotes a return and returns to category you specify\n"
          "!split amount category -- splits an amount from original amount into category\n")
    input("\nPress enter to get back to transactions.")
    return


def num_error():
    print("INVALID COMMAND. Please enter a valid number.")
    input("Press enter to try again.")
    return
