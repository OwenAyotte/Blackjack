from blackjack_classes import Deck, Hand
from utility import clear_screen, continue_prompt, unpack_hands, sort_hands, BettingManager
from game_logic import play_hand, calculate_blackjack_payout, dealer_hits, handle_misc_hands
from constants import MAX_DECKS

"""
Simple playable Blackjack program with betting features.
This program is designed as a skeleton from which a program for collecting data on the preformance blackjack algorithms can be built, 
however for ease of testing (and also just for the sake of having a more tangible project), it is fully playable.

I understand that this is by no means particularly clean code, 
but as a first stab at coding outside the confines of a University assignment with extensive guidelines,
it allows me to see where my weak points are in terms of structure.


"""


def blackjack_round(deck, betting_manager):
    """Runs a round of blackjack, returns payout for the player."""
    payout = 0
    clear_screen()


    #initalizes hands for dealer and player
    player_hand = Hand(deck, "PLAYER")
    dealer_hand = Hand(deck, "DEALER", hidden=True)
    
    


    completed_hands = play_hand(player_hand, dealer_hand, deck, betting_manager) 
    #returns a list of hands,w/ multiple hands/sublists if the player has split

    all_hands = unpack_hands(completed_hands) #unpacks all hands into a single list of hands



 
    busted_hands = [] #list of hands that are busts
    non_busted_hands = [] #list of hands that are not busts, as well as not blackjacks
    blackjack_hands = [] #list of hands that are blackjacks

    for hand in all_hands: #for each hand, check if it is a bust     
        if hand.check_bust():
            busted_hands.append(hand)
        elif hand.blackjack_check():
            blackjack_hands.append(hand)
        else:
            non_busted_hands.append(hand)

            
    
    dealer_hand.unhide()
    print("\nDealer flips over their card.")
    print(dealer_hand)
    print()


    payout += calculate_blackjack_payout(blackjack_hands, dealer_hand, betting_manager) #calculates payout for blackjacks, if any exist

    if not blackjack_hands and dealer_hand.blackjack_check(): #if dealer is the only one with a blackjack, print message and return 0 payout
            print("Dealer has a Blackjack! All your hands lose!")
            return 0




    if busted_hands: #if there are any busts, print them before progessing to non-busts
        print("Busted hand(s):")
        for hand in busted_hands:
            print(hand)
        print()

    if not non_busted_hands: return payout #if there are no non-busted hands, payout is returned early instead of going through the rest of the payout checks
    

    #dealer hits, if they bust, payout is returned early
    dealer_bust_payout = dealer_hits(dealer_hand, non_busted_hands, betting_manager) 
    if dealer_bust_payout != 0: 
        payout += dealer_bust_payout 
        return payout 
    
            



    sorted_hands = sort_hands(non_busted_hands, dealer_hand) #sorts hands into losing, tieing and winning hands

    for i in range(len(sorted_hands)):
        payout += handle_misc_hands(sorted_hands[i], i, betting_manager)
                

    return payout

def game(betting_manager, deck):
    """Runs blackjack with the same deck and bet amount until the player either requests to stop or runs out of money.
    Returns True if the player wants to continue playing, False if they want to stop."""
    clear_screen()
    print(f"${betting_manager.get_bet()} has been set as been deducted from your balance.")
    while True:     
        
        if betting_manager.make_bet(round_starting = True): #checks if bet is can be made
            round_payout = blackjack_round(deck, betting_manager)

            continue_prompt() #waits for user to press enter before clearing the screen
            betting_manager.payout(round_payout) 
            
        else:
            print("You don't have enough to keep betting!")
            return True
        
        print()
        print(f"You currently have ${betting_manager.get_balance()} and are betting ${betting_manager.get_bet()}.")

        print('Play again? ("s" - Settings | "q" - Quit Playing | other - Next Round)')
        play_again = input('> ').strip().lower()

        if play_again == "s": #returns to main menu
            clear_screen()
            return True
        
        elif play_again == "q":
            clear_screen()
            return False
    
def bet_input_validation(bet, betting_manager):
    """Validates the bet input (handles cases where input is non-int, negative and exceeding balance). 
    Returns True if valid, False if not. Additionally, prints an error message if the bet is invalid."""
    try:
        bet = int(bet)  # Converts bet to int
    except ValueError:
        print("Bet must be an integer!")
        return False

    if bet <= 0:
        print("Bet must be greater than 0!")
        return False

    if bet > betting_manager.get_balance():
        print("You cannot bet more than you have!")
        return False

    betting_manager.set_bet(bet)
    return True
        

def deck_input_validation(deck_amount, deck_exists):
    """Validates the deck amount input (handles cases where input is non-int, negative and exceeding max).
    Returns True if valid, False if not. Additionally, prints an error message if the deck amount is invalid."""

    if deck_amount == "": #if the input is empty, check if deck exists, if so do not replace it
        if deck_exists:
            return True
        else: 
            print("No deck exists! Please input a deck amount.")
            return False
    try:
        deck_amount = int(deck_amount) 
    except ValueError:
        print("Deck amount must be an integer!")
        return False

    if deck_amount <= 0:
        print("Deck amount must be greater than 0!")
        return False

    if deck_amount > MAX_DECKS: 
        print(f"Deck amount must be less than or equal to {MAX_DECKS}!")
        return False

    return True


def main():
    clear_screen()
    print("Welcome to Blackjack!")
    betting_manager = BettingManager() #initializes betting manager 
    still_playing = True
    deck_exists = False #used to check if a deck has been created, so that the user can change the deck amount without having to restart the game

    while still_playing:

        bet_query = f"You have ${betting_manager.get_balance()}. How much would you like to bet? > $"
        deck_query = f"How many decks would you like to play with? (max {MAX_DECKS} | leave empty to continue using prior deck) > "


        #get information regarding bets
        bet = input(bet_query)
        while not bet_input_validation(bet, betting_manager):
            bet = input(bet_query)
        print(f"${betting_manager.get_bet()} has been been deducted from your balance.")
        print()


        
        deck_amount = input(deck_query)
        while not deck_input_validation(deck_amount, deck_exists):
            deck_amount = input(deck_query)

       #in the case that the user has input "", no new deck is generated, allowing for card-counting strategies to be used after a change in betting amount 
        if deck_amount != "": 
            deck = Deck(int(deck_amount))
            deck_exists = True

        

        still_playing = game(betting_manager, deck)
        print()


        

        if betting_manager.get_balance() < 1: #<1 is used rather than <=0 to avoid issues where a player with $0.50 is unable to bet an integer
            print("You have run out of money! Game over.")
            still_playing = False


if __name__ == "__main__":
    main()


    