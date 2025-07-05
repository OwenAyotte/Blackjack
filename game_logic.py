from blackjack_classes import Hand
from constants import BLACKJACK_PAYOUT_RATIO, TIE_PAYOUT_RATIO, WIN_PAYOUT_RATIO, LOSS_PAYOUT_RATIO
from utility import continue_prompt, clear_screen



         
def split(deck, hand):
    """NOT TO BE USED DIRECTLY, USE split_hand INSTEAD!
    Takes a hand, and returns two hands featuring the cards from it as well as an additional card.
    Only works if the hand only has two cards and cards share a value (not to be confused with sharing a rank)."""
    if len(hand.cards) != 2:
        print("Cannot split hand with more than 2 cards!")
        return None

    if hand.cards[0].get_value() != hand.cards[1].get_value():
        print("Cannot split hand with different card values!")
        return None

    #creates two new hands with the first card of the original hand
    first_hand = Hand(deck, "PLAYER", starting_card=hand.cards[0])
    second_hand = Hand(deck, "PLAYER", starting_card=hand.cards[1])

    return [first_hand, second_hand]


def split_hand(hand, dealer_hand, deck, betting_manager):
    """Calls split function, if successful, allows each split hand to be played and returns them in a list.""" 


    if betting_manager.can_increment_split() == False: #if player has already split 3 times
        print("You cannot split this hand! You have already split this round.")
        continue_prompt()
    elif betting_manager.can_make_bet() == False: 
        print("You cannot split this hand! You do not have enough money to make a bet.")
        continue_prompt()
    else:
        new_hands = split(deck, hand) #attempts to split the hand, returns two new hands if successful, None if not
        if new_hands is None:
            print("You cannot split this hand! You do not have enough money to make a bet.")
            continue_prompt()
        else:
            betting_manager.make_bet() 
            #Recursively calls play_hand on the two new hands
            first_hand = play_hand(new_hands[0], dealer_hand, deck, betting_manager) 
            second_hand = play_hand(new_hands[1], dealer_hand, deck, betting_manager)
            return [first_hand, second_hand] #list will be unpacked into individual hands in blackjack_round
        
    return None #if the split was not successful, return None
        
        

def calculate_blackjack_payout(blackjack_hands, dealer_hand, betting_manager):
    """Manages payout in the case of a blackjack beng possessed by the user. 
    Returns payout for all user hands that are blackjacks."""
    blackjack_payout = 0 

    if blackjack_hands: #if there are any blackjacks in the user's hands, print them before progessing to non-busts
        print("Blackjack hand(s):")
        for hand in blackjack_hands:
            print(hand)

        if dealer_hand.blackjack_check():
            #if the dealer also has a blackjack, all blackjacks award the inital betting amount back
            
            for hand in blackjack_hands:
                #note that this function doesn;t check if the hand is doubled down, as blackjacks are not allowed to be doubled down
                #since doing so would require a 3rd card to be drawn
                blackjack_payout += betting_manager.get_bet()  * TIE_PAYOUT_RATIO
                blackjack_payout = round(blackjack_payout) #rounds payout to nearest dollar
                #rounding to the nearest dollar is only done with blackjacks, as otherwise the payout is already an integer
            print("Dealer has a Blackjack!")
            print(dealer_hand)
            print(f"Dealer has a Blackjack! Your Blackjack(s) push! You make ${blackjack_payout} back.")
            

        else:
            
            for hand in blackjack_hands:
                blackjack_payout += betting_manager.get_bet() * BLACKJACK_PAYOUT_RATIO
                blackjack_payout = round(blackjack_payout) #rounds payout to nearest dollar
            print(f"Your Blackjack(s) win! You get a 3:2 payout, netting ${blackjack_payout}!")
            
        print()

        
    
    return blackjack_payout 

def dealer_hits(dealer_hand, non_busted_hands, betting_manager):
    """Allows the dealer to hit until they have at least 17.
    Returns payout of all non-busted hands if dealer busts, otherwise 0."""

    payout = 0 

    dealer_has_hit= False #used to check if dealer has hit at least once, used to avoid re-printing dealer hand if it isnt modified 
    if dealer_hand.get_total() < 17: #if dealer has less than 17 dealer must hit
        print(f"Dealer begins hitting!")
        print("...")
    while dealer_hand.get_total() < 17: #dealer must hit until they have at least 17
        dealer_hand.draw()
        dealer_has_hit = True 
    

        if dealer_hand.check_bust(): #if dealer busts, all user hands are winners
            print(dealer_hand)
            print()
            print("Dealer busts! All your non-busted hands win!\n")
            print("Winning hands:")
            for hand in non_busted_hands:
                print(hand)
                payout += betting_manager.get_bet() * hand.get_doubled_down() * WIN_PAYOUT_RATIO 
            return payout #ends round, all non-busted hands win
        

    
    if dealer_has_hit: #if dealer has hit, print their new hand
        print(dealer_hand)
        print()

    return 0


def handle_misc_hands(hands, multiplier, betting_manager):
    """Prints the hands given to it, scores it, and returns the payout. 
    Handles hands that are scored after the dealer has hit, opposed to ones such as blackjacks and busts."""
    if not hands:
        return 0
    
    hand_types = {LOSS_PAYOUT_RATIO: "Losing Hand(s):", TIE_PAYOUT_RATIO: "Tied Hand(s):", WIN_PAYOUT_RATIO: "Winning Hand(s):"} #dictionary to map hand types to strings

    payout = 0    
    print(hand_types[multiplier])
    for hand in hands:
        print(hand)
        #multiplier inuitively handles win/push/tie payout amounts
        payout += betting_manager.get_bet() * hand.get_doubled_down() * multiplier 
    hand_messages = {LOSS_PAYOUT_RATIO: "You make nothing from these hands.",
                    TIE_PAYOUT_RATIO: f"You push with these hands, making your bet of ${betting_manager.get_bet()} back each.",
                    WIN_PAYOUT_RATIO: f"You win ${payout}!"}
    print(hand_messages[multiplier])
    print()

    return payout

        
def dealer_hits(dealer_hand, non_busted_hands, betting_manager):
    """Allows the dealer to hit until they have at least 17.
    Returns payout of all non-busted hands if dealer busts, otherwise 0."""

    payout = 0 

    dealer_has_hit= False #used to check if dealer has hit at least once, used to avoid re-printing dealer hand if it isnt modified 
    if dealer_hand.get_total() < 17: #if dealer has less than 17 dealer must hit
        print(f"Dealer begins hitting!")
        print("...")
    while dealer_hand.get_total() < 17: #dealer must hit until they have at least 17
        dealer_hand.draw()
        dealer_has_hit = True 
    

        if dealer_hand.check_bust(): #if dealer busts, all user hands are winners
            print(dealer_hand)
            print()
            print("Dealer busts! All your non-busted hands win!\n")
            print("Winning hands:")
            for hand in non_busted_hands:
                print(hand)
                payout += betting_manager.get_bet() * hand.get_doubled_down() * WIN_PAYOUT_RATIO 
            return payout #ends round, all non-busted hands win
        

    
    if dealer_has_hit: #if dealer has hit, print their new hand
        print(dealer_hand)
        print()

    return 0




def play_hand(hand, dealer_hand, deck, betting_manager):
    """Allows player to hit, double down, split, or stand.
    Returns the payout for the player."""
    
    clear_screen()
    OPTION_CHOICER = """What would you like to do?\n\t1. Hit\n\t2. Double Down\n\t3. Split\n\t4. Stand"""
    

    round_start = True
    while (hand.check_standing() == False): #busting/reaching 21 sets standing to True (check draw card method of Hand), so both cases are covered
        clear_screen()
        deck.print_remaining_cards(round_start) #prints remaining cards in deck
        round_start = False #after the first loop, round_start is set to False, so the message is not printed again

        print(hand)
        print(dealer_hand)
        print()


        print(OPTION_CHOICER)

        player_selection = input("> ")
        clear_screen()

        if player_selection == "1": #HIT
            #Draw card
            hand.draw()

        elif player_selection == "2": #DOUBLE DOWN
            if betting_manager.make_bet(): #ensures that the player has enough money to double down
                hand.draw()
                hand.double_down()
                hand.stand() #automatically stands after doubling down
                print(deck.remaining_cards())
                print("You have doubled down!")
                print(f"{hand}")
                continue_prompt()
            else:
                print("You cannot double down! You do not have enough money to make a bet.")
                continue_prompt()

           

        elif player_selection == "3": #SPLIT
            #split hand function plays the two new hands to completion
            #so function output can be returned directly in the case where the split is successful
            split_result = split_hand(hand, dealer_hand, deck, betting_manager)
            if split_result is not None:
                return split_hand(hand, dealer_hand, deck, betting_manager)
            
            

        elif player_selection == "4": #STAND
            #Set standing to True, ends loop and lets dealer start hitting
            hand.stand()

    if hand.check_bust():
        deck.print_remaining_cards()
        print(f"{hand}")
        print(f"{dealer_hand}\n")
        continue_prompt("Bust! Press enter to continue.")

    elif hand.blackjack_check():
        deck.print_remaining_cards()
        print(f"{hand}")
        print(f"{dealer_hand}\n")
        continue_prompt("Blackjack! Press enter to continue.")

    elif hand.get_total() == 21:
        deck.print_remaining_cards()
        print(f"{hand}")
        print(f"{dealer_hand}\n")
        continue_prompt("You have 21! Press enter to continue.")
        

        


    return hand 