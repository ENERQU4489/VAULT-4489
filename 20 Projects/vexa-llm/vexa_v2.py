import random
import time
import re
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

console = Console()

class VexaMarkovAI:
    def __init__(self, order=1):
        self.order = order
        self.model = defaultdict(list)
        self.words = []
        self.word_counts = Counter()

    def train(self, text):
        # Czyszczenie i tokenizacja
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        self.words = tokens
        self.word_counts.update(tokens)

        console.print("[bold cyan]Vexa-LLM:[/bold cyan] Rozpoczynam trening na dostarczonym tekście...")
        
        # Budowanie łańcucha Markowa
        for i in track(range(len(tokens) - self.order), description="Przetwarzanie struktury języka..."):
            state = tuple(tokens[i:i + self.order])
            next_word = tokens[i + self.order]
            self.model[state].append(next_word)
            time.sleep(0.01)  # Efekt "myślenia"

    def generate(self, length=10, seed=None):
        if not self.model:
            return "Nie mam jeszcze wiedzy..."

        if seed and tuple(seed.lower().split()[-self.order:]) in self.model:
            state = tuple(seed.lower().split()[-self.order:])
        else:
            state = random.choice(list(self.model.keys()))

        output = list(state)
        for _ in range(length):
            next_options = self.model.get(state)
            if not next_options:
                break
            next_word = random.choice(next_options)
            output.append(next_word)
            state = tuple(output[-self.order:])

        return " ".join(output)

    def visualize_stats(self):
        # Tabela w terminalu
        table = Table(title="Statystyki Treningu Vexa-LLM")
        table.add_column("Słowo", style="magenta")
        table.add_column("Wystąpienia", justify="right", style="green")

        for word, count in self.word_counts.most_common(10):
            table.add_row(word, str(count))
        
        console.print(table)

        # Wykres Matplotlib
        common = self.word_counts.most_common(15)
        labels, values = zip(*common)
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color='skyblue')
        plt.title('Częstotliwość słów w zestawie treningowym')
        plt.xticks(rotation=45)
        plt.tight_layout()
        console.print("[yellow]Otwieram okno wizualizacji danych...[/yellow]")
        plt.show()

def main():
    # Przykładowy krótki wiersz (Wisława Szymborska - "Nic dwa razy")
    poem = """
    Nic dwa razy się nie zdarza
    i nie zdarzy. Z tej przyczyny
    zrodziliśmy się bez wprawy
    i pomrzemy bez rutyny.

    Choćbyśmy uczniami byli
    najtępszymi w szkole świata,
    nie będziemy repetować
    żadnej zimy ani lata.

    Żaden dzień się nie powtórzy,
    nie ma dwóch takich samych nocy,
    dwóch tych samych pocałunków,
    dwóch tych samych spojrzeń w oczy.
    """

    vexa = VexaMarkovAI(order=1)
    
    console.print(Panel.fit("VEXA-LLM v2.0 - Primitive AI Engine", style="bold magenta"))
    
    vexa.train(poem)
    vexa.visualize_stats()

    console.print("\n[bold green]System gotowy![/bold green] Vexa nasiąknęła poezją.")
    console.print("(Wpisz 'wyjdź', aby zakończyć)\n")

    while True:
        user_input = console.input("[bold blue]Ty:[/bold blue] ").lower().strip()
        
        if user_input == 'wyjdź':
            break
        
        # Generowanie odpowiedzi na bazie słów kluczy z wejścia lub losowo
        response = vexa.generate(length=random.randint(5, 12), seed=user_input)
        console.print(f"[bold cyan]Vexa-LLM:[/bold cyan] {response}...")

if __name__ == "__main__":
    main()
