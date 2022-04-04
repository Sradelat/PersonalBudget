import csv
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl


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

    while True:
        path = input("Please enter the file path: ")  # csv file downloaded from website -sorry will not provide mine :)
        try:  # for valid file  # TODO add confirmation upon showing file contents?
            df = pd.read_csv(path, delimiter=",",
                             parse_dates=True, skipinitialspace=True)
            break
        except FileNotFoundError as error:  # catch invalid file entered
            print(error)

    df = df.loc[df["Description"] != "AUTOPAY PAYMENT - THANK YOU"]  # remove bill payments for total accuracy
    df = df.iloc[::-1].reset_index(drop=True)  # reverse the df
    df["Description"] = df.Description.str.split().str[:].apply(lambda x: " ".join(x))  # goodbye whitespace
    print(df)  # display for user
    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]
    all_total = round(df["Amount"].sum(), 2)  # sum of transactions
    statement_date = f"{start_date} - {end_date}"
    print(f"AMEX STATEMENT DATE: {statement_date} ")  # show statement date range
    print(f"OVERALL TOTAL: {all_total}")  # show total
    input("\nPress enter to initiate manual categorizing.")
    # categories = {"food": 308.65, "gas": 422.42, "life": 1683.77, "pets": 531.58}  # for testing purposes
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
            elif answer.split(" ")[0] == "!delcat":  # deletes category and forwards remaining value-don't want in plot
                if answer.split()[1] not in categories:  # catches invalid category
                    print("ERROR. INVALID CATEGORY. Please try again.")
                    input("Press enter to acknowledge.")
                    continue
                elif categories[answer.split()[1]] != 0:
                    print(f"\nWARNING! Category {answer.split()[1]} has a value of "
                          f"{categories[answer.split()[1]]}.")
                    print("Would you like to transfer this amount into another category before deletion?"
                          "\n1. Yes"
                          "\n2. No")
                    while True:
                        cattrans = input(">")
                        if cattrans == "1":  # delete cat with transfer
                            while True:
                                print(f"\nWhich category would you like to add {categories[answer.split()[1]]} to?")
                                new_cats = ""
                                transamount = categories[answer.split()[1]]  # pull amount before deletion
                                for k, v in categories.items():
                                    if k != answer.split()[1]:  # exclude category to be deleted
                                        new_cats += f"[{k}] "  # generate updated categories
                                print(f"Valid categories: {new_cats}")  # show updated categories
                                add_to = input(">")  # specified category
                                success = update_category_value(add_to, categories, transamount)
                                if success is True:  # delete category and continue
                                    categories.pop(answer.split()[1])  # deletes category
                                    print(f"\nCategory {answer.split()[1]} has been deleted.")
                                    break
                                if success is False:  # try again
                                    continue
                            break
                        elif cattrans == "2":  # delete cat without transfer
                            categories.pop(answer.split()[1])
                            print(f"Category {answer.split()[1]} has been deleted.")
                            break
                        else:
                            print("ERROR. Invalid command. Enter a number, 1 or 2.")
                            continue
            elif answer.split(" ")[0] == "!return":  # if transaction is a money back return
                try:
                    categories[answer.split(" ")[1]] = round(float(categories[answer.split(" ")[1]]) +
                                                             float(amount), 2)
                    break
                except KeyError:  # invalid category
                    print("ERROR. Invalid category. Expected form for this command: !return category")
                    input("Press enter to acknowledge.")
                    continue
            elif answer.split(" ")[0] == "!split":  # splits specified amount into specified category
                try:
                    split = float(answer.split()[1])  # answer is passed to fx not split
                except (ValueError, IndexError):  # catches if amount and category are swapped (wrong format)
                    print("ERROR: Unexpected format. Expected format for this command: !split amount category")
                    input("Press enter to acknowledge.")
                    continue
                if split > float(amount):  # catches entered amounts larger than actual amount
                    print("ERROR: Split amount entered exceeds original amount.")
                    input("Press enter to acknowledge.")
                    continue
                if len(str(answer).split()[1].split(".")[1]) > 2:  # catches if too many decimals are entered
                    print("ERROR. Too many decimal places entered.")
                    input("Press enter to acknowledge.")
                    continue
                else:
                    try:
                        amount = split_transaction(answer, amount, categories)  # returns remaining amount
                        continue
                        # TODO other command errors
                        #  combine split errors into split fx?
                        #  condense errors by assigning .split values before passing into fx?
                    except IndexError:  # catches if .split values are not correct amount (3) as in format below
                        print("ERROR. Unexpected format. Expected format for this command: !split amount category")
                        input("Press enter to acknowledge.")
                        continue
                    except KeyError:  # catches invalid entered category
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

    # PIE CHART
    plt.figure(figsize=(7, 7))
    ax = plt.subplot(111)
    ax.pie(list(categories.values()), labels=list(categories.keys()))
    ax.axis("equal")
    plt.show()

    # WRITE TO EXCEL FILE
    excel_df = pd.DataFrame(data=categories, index=[0])
    excel_df = excel_df.T
    print(excel_df)
    excel_df.to_excel("Budget.xlsx")
    print("Excel file has been updated.")
    input("\nPress enter to return to home screen.")
    home()
    return


# def wells_fargo():  # Uses Wells Fargo CSV - NEED TO CHANGE OVER TO NEW CHASE ACCOUNT
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
          "!delcat category       -- deletes category you specify\n"
          "!totals                -- shows current totals for each category\n"
          "!return category       -- denotes a return and returns to category you specify\n"
          "!split amount category -- splits an amount from original amount into category\n")
    input("\nPress enter to get back to transactions.")
    return


def num_error():
    print("INVALID COMMAND. Please enter a valid number.")
    input("Press enter to try again.")
    return
