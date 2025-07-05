import random
"""Contains classes pertaining to the cards in a game of blackjack."""


class Deck:
    def __init__(self, amount=1):
        """Creates a deck, then appends it to self until quantity of decks is reached."""
        self.amount = amount
        self.cards = []

        self.standard_deck = []

        
        #creates a standard deck of cards, with 13 ranks and 4 suits
        #multiple standard decks are combined to create the full deck if amount > 1
        for rank in range(13): #13 ranks
            for suit in range(4): #4 suits
                new_card = Card(rank+1, suit)
                self.standard_deck.append(new_card)
        


        #the only reason this is a method instead of just being in the __init_
        #is because it needs to be used if the deck is empty and needs to be reconstructed
        self.construct_deck() 

    def draw_card(self):
        """Pops random card from deck and returns it. In the case that the deck is empty, recreates the deck beforehand."""

        if len(self.cards) != 0: #if the deck is empty, reconstruct it
            card_index = random.randrange(len(self.cards))
        else:
            self.construct_deck() #ideally, there would be some form of prompt to the user to reconstruct the deck, 
            #but due to the amount of unique contexts that prompt would have to appear in, making them all fit the UI is beyond my current scope
            card_index = random.randrange(len(self.cards))

        return self.cards.pop(card_index)
    
    def construct_deck(self):
        """Creates the deck by appending the standard deck to self.amount times."""

        for i in range(self.amount):
            self.cards += self.standard_deck

    def print_remaining_cards(self, round_start=False):
        """Returns a message showing how many cards are left in the deck.
        If round_start is True, the message also contains a round starting message."""
        #in retrospect this should be a function in game_logic.py (which would allow the message to display information such as balance as well)
        #however the primary pupose of this program is a skeleton for an automated program without print statements so it's not worth overhauling the code

        round_start_message = "ROUND START!"
        deck_message = f"DECK: {len(self.cards):>3}"
        if round_start:
            print(f"{round_start_message:<20}{deck_message} cards")
        else:
            print(f"{'':<20}{deck_message} cards")

    def get_card_amount(self):
        """Returns the number of cards left in the deck."""
        return len(self.cards)
    
        

    
class Hand:
    def __init__(self, deck, name, hidden=False, starting_card=None):
        """Initializes hand, sets name/source deck/hidden status and draws two cards from deck."""
        self.cards = []
        self.deck = deck
        self.name = name
        self.standing = False
        self.doubled_down = 1 #doubled_down is 1 if player did not double down, 2 if they did
        self.hidden = hidden #hidden is true if the dealer's second card is hidden, false if it is not

        if starting_card != None: #allows for a starting card to be passed in, used for split hands
            self.cards.append(starting_card)
            try:
                self.draw()
            except ValueError:
                raise 
        else:
            for i in range(2):
                try:
                    self.draw()
                except ValueError:
                    raise
    
    def draw(self):
        """Appends card drawn from deck to list of cards."""
        try:
            self.cards.append(self.deck.draw_card()) 
        except ValueError:
            raise 

        if self.get_total() >= 21:
            self.standing = True #if the hand is a bust or 21, set standing to True

    def unhide(self):
        """Sets hidden to false, revealing dealers hidden card"""
        self.hidden = False

    def __str__(self):
        name = f"{self.name}: "

        printed_cards = ""

        #appends cards to string
        if self.hidden: #in the case that the dealers second card is hidden, replace second card with [???]


            printed_cards += str(self.cards[0])+"\x1b[39m[???]\x1b[0m" 
            #colour code of [???] is set to default, this is because the cards' color codes count as characters for the purposes of alignment
            #so in order for everything to be standardized a superflous color code is added
        else:
            for card in self.cards:
                printed_cards += str(card)

        
        padding = self.get_padding() #gets padding because we can't do this with normal string formatting due to the color codes 


        total = f"TOTAL: {self.get_total():>2}"
        printed_hand = f"{name}{printed_cards}{padding}{total:>2}"

        return printed_hand
    
    def get_padding(self):
        """Returns a string consisting of whitespace representing the required padding between the cards and the total when printed."""
        padding = 30
        for card in self.cards:
            padding -= 5 #card has 5 visible characters when printed. can't use len() because of the color codes

        if padding <= 5: #ensures padding has a minimum length of 5, 
            padding = 5

        return " " * padding  #returns string of whitespace with length of padding



    
    def blackjack_check(self):
        """Returns True if hand is a Blackjack (sums to 21 with only two cards)
        Otherwise returns False"""
        return (self.get_total() == 21 and len(self.cards) == 2)
    
    def check_bust(self):
        """Returns True if hand is a bust (sums to more than 21), otherwise returns False
        Also sets standing to True if hand is a bust."""
        if self.get_total() > 21:
            self.standing = True
        return self.get_total() > 21
    
    def check_standing(self):
        """Returns True if hand is standing, otherwise returns False"""
        return self.standing
    
    def double_down(self):
        """Doubles the bet for the hand, and returns True if successful, False if not."""
        self.doubled_down = 2

    def stand(self):
        """Sets standing to True, ending the round for the hand."""
        self.standing = True

    def get_doubled_down(self):
        """Returns the doubled down value of the hand, which is 1 if the player did not double down, and 2 if they did."""  
        return self.doubled_down
    
    def get_total(self):
        """Calculates score of hand by summing their values. 
        Reduces total by 10 for every Ace until total is equal to or less than 21."""
        hand_total = 0
        ace_count = 0

        if self.hidden == True: #in the case that the dealers card is hidden, return the value of their only unhidden card
            return self.cards[0].get_value()


        #sums values of the cards, and counts Aces
        for card in self.cards:
            hand_total += card.get_value()
            if card.get_value() == 11:
                ace_count += 1

        #simulates recategorizing Aces as 1s instead of 11s.
        #due to the hand total being the largest possible value without exceeding 21, 
        #soft 17s are always read as 17 and stop dealer from hitting
        while (hand_total > 21) and (ace_count > 0):
            if ace_count != 0:
                ace_count -= 1
                hand_total -= 10
 
        return hand_total




        
class Card:
    #allows attributes of card to be displayed and used for calculation
    suits = ["♥", "♦", "♣", "♠"]
    readable_ranks = {1:"A", 11:"J", 12:"Q", 13:"K"}
    special_values = {1:11, 11:10, 12:10, 13:10}

    def __init__(self, rank, suit):
        self.rank = rank #1-13 (Ace-King)
        self.suit = suit #0-3 (index for list of suits)
        

    def __str__(self):
        """Returns string containing the rank and suit of the card, after converting both to readable form.
        Prints in different colors depending on the suit."""

        suit_colours = {
            0: "\033[31m",  # Red for Hearts
            1: "\033[33m",  # Yellow for Diamonds
            2: "\033[32m",  # Green for Clubs
            3: "\033[34m",  # Blue for Spades
        }

        rank_str = str(Card.readable_ranks.get(self.rank, self.rank)) #converts rank to string interpretation of int/character
        rank_str = f"[{rank_str:>2}{Card.suits[self.suit]}]" #combines rank with suit and adds align so strings with "10" don't take up extra space 
        return suit_colours[self.suit] + rank_str + "\033[0m"  #Returns string with suit color formatting
    
    def get_value(self):
        """Returns rank of the card, unless the rank corresponds to a card with a special value (Aces and Face Cards). 
        In that case, the value is taken from the special values dictionary"""
        return Card.special_values.get(self.rank, self.rank) #if special value is not found, returns second value