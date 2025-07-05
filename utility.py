import os
from blackjack_classes import Deck, Hand
from constants import STARTING_BALANCE, WIN_PAYOUT_RATIO, TIE_PAYOUT_RATIO, LOSS_PAYOUT_RATIO

"""Utility functions for the blackjack program.
These functions are used to clear the screen, prompt the user to continue, unpack hands, and manage betting.
"""

def clear_screen():
    """Clears the console screen."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def continue_prompt(message_text="Press enter to continue."):
    """Prompts the user to press enter to continue, before clearing the screen.
    Prompt has a default message, but can be changed by passing a string to the function."""
    print(message_text)
    input()
    clear_screen()

def unpack_hands(packed_hands):
    """Unpacks a list of hands (which may contain sublists of hands recursively) into a single list of hands with no sublists."""
    unpacked = []
    if isinstance(packed_hands, Hand):#if no unpacking is needed, return the hand
        unpacked.append(packed_hands)
        return unpacked
    
    for hand in packed_hands:
        if isinstance(hand, Hand): #in the case that the hand is a single hand, append
            unpacked.append(hand)

        elif isinstance(hand, list): #due to the possibility of splitting hands, unpack_hands may receive a list of hands
            #if the hand is a list of hands, unpack each hand and append 
            for sub_hand in hand:
                all_subhands = unpack_hands(sub_hand)
                unpacked += all_subhands

    return unpacked

class BettingManager:
    """Manages the player's money, allowing payouts and bets to be made."""
    def __init__(self):
        self.balance = STARTING_BALANCE 
        self.bet = 0 
        self.split_amount = 0 #Amount of times user has split

    def set_bet(self, bet):
        """Sets the bet amount for the player. Returns False if the bet is invalid, True if it is valid."""
        if bet > self.balance:
            print("You cannot bet more than you have!")
            return False
        elif bet <= 0:
            print("Bet must be greater than 0!")
            return False
        else:
            self.bet = bet
            return True

    def get_bet(self):
        """Returns the current bet amount."""
        return self.bet
    
    def get_balance(self):
        """Returns the current balance of the player."""
        return self.balance
    
    def make_bet(self, round_starting=False):
        """Subtracts the bet amount from the player's money.
        If bet exceeds balance, returns False and prints a rejection message.
        Rejection message varys depending on whether the round has started or not."""
        if self.bet <= self.balance:
            self.balance -= self.bet
            return True
        else:
            if round_starting: #if the round is starting, prompt for a new bet
                print("You cannot bet more than you have!")
            #error message is printed outside of this function if user is trying to double down or such
            return False
        

    def can_make_bet(self):
        """Checks if the player can make a bet, i.e. if they have enough money to cover the bet.
        Returns True if they can, False if they cannot.

        In most cases, make_bet() is tidier to use, but for cases such as splitting where the requirements for an action are more complex
        than just having enough money, this function can be used to check without automatically making a bet.
        """
        return self.balance >= self.bet and self.bet > 0
        
    def increment_split(self):
        """Increments the split amount by 1. Keeps track of how many times the player has split their hand."""
        self.split_amount += 1
        
    def can_increment_split(self):
        """Checks if the player can increment the split amount, i.e. if they have enough money to cover the bet.
        Returns True if they can, False if they cannot."""
        return self.split_amount < 3


    
    def payout(self, amount):
        """Adds the amount to the player's balance. Prints a message indicating the payout.
        Additionally, resets the split amount to zero, as the round has ended."""
        self.balance += amount
        print(f"You have gained ${amount}. Your new balance is ${self.balance}.")
        self.split_amount = 0 #resets the split amount to zero, as the round has ended

        

def sort_hands(unsorted_hands, dealer_hand):
    """Sorts hands into a dictionary, with the keys being whether they beat the dealer, lose to the dealer, or tie with the dealer.
    Returns a dictionary with each key corresponding to a list of hands."""
    sorted_hands =  {LOSS_PAYOUT_RATIO: [], TIE_PAYOUT_RATIO: [], WIN_PAYOUT_RATIO: []} #returns a dictionary with empty lists for each key, to be filled in later


    for hand in unsorted_hands: 
        if hand.get_total() > dealer_hand.get_total():
            sorted_hands[WIN_PAYOUT_RATIO].append(hand)
        elif hand.get_total() < dealer_hand.get_total():
            sorted_hands[LOSS_PAYOUT_RATIO].append(hand)
        else:
            sorted_hands[TIE_PAYOUT_RATIO].append(hand)

    return sorted_hands

