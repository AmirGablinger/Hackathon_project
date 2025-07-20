import random

class BlackjackGame:
    def __init__(self, bet, player=None, dealer=None, game_over=False, result=None):
        self.bet = bet
        self.player = player or [self.deal_card(), self.deal_card()]
        self.dealer = dealer or [self.deal_card()]
        self.game_over = game_over
        self.result = result

    def deal_card(self):
        card = random.randint(1, 13)
        return 10 if card > 10 else card

    def calculate_total(self, cards):
        total = sum(cards)
        if 1 in cards and total + 10 <= 21:
            total += 10
        return total

    def hit(self):
        self.player.append(self.deal_card())
        if self.calculate_total(self.player) > 21:
            self.game_over = True
            return 'bust'
        return 'continue'

    def stand(self):
        while self.calculate_total(self.dealer) < 17:
            self.dealer.append(self.deal_card())

        player_total = self.calculate_total(self.player)
        dealer_total = self.calculate_total(self.dealer)

        if player_total > 21:
            outcome = 'lose'
        elif dealer_total > 21 or player_total > dealer_total:
            outcome = 'win'
        elif player_total == dealer_total:
            outcome = 'draw'
        else:
            outcome = 'lose'

        self.game_over = True
        self.result = {
            'outcome': outcome,
            'player_total': player_total,
            'dealer_total': dealer_total,
        }

        return outcome
