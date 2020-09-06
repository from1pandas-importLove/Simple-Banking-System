import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS card''')
conn.commit()
cur.execute('''CREATE TABLE card(
               id INTEGER,
               number TEXT,
               pin TEXT,
               balance INTEGER DEFAULT 0);''')


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0


def main_menu():
    print('1. Create an account\n2. Log into account\n0. Exit')


def account_operation():
    print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')


class SBS:
    def __init__(self):
        self.accounts = {}
        self.active = 1
        self.active_account = ''
        self.counter = 0

    def new_account(self):
        card_number = ''
        while card_number == '':
            card_number = '400000' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
            control_digit = [int(card_number[x]) if x % 2 else int(card_number[x]) * 2 for x in range(len(card_number))]
            control_digit = str((10 - sum([x if x < 10 else x - 9 for x in control_digit]) % 10) % 10)
            card_number += control_digit
            if card_number in self.accounts:
                card_number = ''
        pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        self.accounts[card_number] = pin
        print(f'Your card has been created\nYour card number:\n{card_number}')
        print(f'Your card PIN:\n{pin}')
        balance = 0
        id_ = self.counter
        cur.execute('INSERT INTO card (id, number, pin, balance) VALUES ({}, {}, {}, {})'.format(id_, card_number, pin, balance))
        conn.commit()
        self.counter += 1

    def login(self, account, pin):
        if account in self.accounts and self.accounts[account] == pin:
            print('You have successfully logged in!')
            self.active_account = account
        else:
            print('Wrong card number or PIN!')

    def del_from_dict(self, number):
        del self.accounts[f'{number}']

    def check_membership_in_dict(self, number):
        if number not in self.accounts:
            result = False
        else:
            result = True
        return result



sbs = SBS()
while sbs.active == 1:
    main_menu()
    a = input()

    if a == '0':
        sbs.active = 0
    elif a == '1':
        sbs.new_account()
    elif a == '2':
        print('Enter your card number:')
        cn = input()
        print('Enter your PIN:')
        pn = input()
        sbs.login(cn, pn)
        while sbs.active_account:
            account_operation()
            a = input()
            if a == '0':
                sbs.active_account = ''
                sbs.active = 0
            elif a == '1':
                cur.execute(f'''SELECT balance
                               FROM card
                               WHERE number = {cn}
                               AND pin = {pn};''')
                print(cur.fetchone()[0])
            elif a == '2':
                print('Enter income:')
                income = int(input())
                cur.execute(f'''UPDATE card
                                SET balance = balance + {income}
                                WHERE number = {cn};''')
                conn.commit()
                print('Income was added!')
            elif a == '3':
                print('Transfer')
                print('Enter card number: ')
                try_transfer_card_number = input()
                if not is_luhn_valid(try_transfer_card_number):
                    print('Probably you made a mistake in the card number. Please try again!')
                elif not sbs.check_membership_in_dict(try_transfer_card_number):
                    print('Such a card does not exist')
                elif try_transfer_card_number == cn:
                    print("You can't transfer money to the same account!")
                else:
                    print('Enter how much money you want to transfer:')
                    money = int(input())
                    cur.execute(f'''SELECT balance
                                    FROM card
                                    WHERE number ={cn};''')
                    if cur.fetchone()[0] < money:
                        print('Not enough money!')
                    else:
                        cur.execute(f'''UPDATE card
                                        SET balance = balance - {money}
                                        WHERE number = {cn};''')
                        cur.execute(f'''UPDATE card
                                        SET balance = balance + {money}
                                        WHERE number = {try_transfer_card_number};''')
                        conn.commit()

                        print('Success!')

            elif a == '4':
                cur.execute(f'''DELETE FROM card
                               WHERE number = {cn}''')
                conn.commit()
                sbs.del_from_dict(cn)
                sbs.active_account = ''
                print('The account has been closed!')
            elif a == '5':
                sbs.active_account = ''
                print('You have successfully logged out!')

print('Bye!')