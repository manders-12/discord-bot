import random

class Blackjack():
    def __init__(self):
        self.deck = ['A', 'J', 'K', 'Q', 'J', '10', '9','8','7','6','5','4','3','2']*4
        self.dealer = {'total' : 0, 'cards' : []}
        self.player = {'total' : 0, 'cards' : []}
        self.state = 1
    
    def deal(self):
        for player in [self.dealer, self.player]:
            for i in range(2):
                draw = self.deck.pop(random.randint(0, len(self.deck)-1))
                player['cards'].append(draw)
                player['total'] += self.__cardval(draw)
        if self.player['total'] == 21: self.play('stand')

    def __cardval(self, card):
        match card:
            case 'A': return 11
            case 'K': return 10
            case 'Q': return 10
            case 'J': return 10
            case _: return int(card)

    def play(self, choice):
        if choice == 'hit' and self.player['total'] < 21 and self.state:
            draw = self.deck.pop(random.randint(0, len(self.deck)-1))
            self.player['cards'].append(draw)
            self.player['total'] += self.__cardval(draw)
            if(self.player['total'] > 21 and 'A' in self.player['cards']): self.player['total'] -= 10
        if(choice == 'stand' or self.player['total'] >= 21):
            while(self.dealer['total'] < 17):
                draw = self.deck.pop(random.randint(0, len(self.deck)))
                self.dealer['cards'].append(draw)
                self.dealer['total'] += self.__cardval(draw)
                if(self.dealer['total'] > 21 and 'A' in self.dealer['cards']): self.dealer['total'] -= 10
            self.state = 0


            


