import random

def simple_vexa_ai():
    print("Vexa-LLM: Cześć! Jestem Twoim prymitywnym AI. O czym chcesz porozmawiać?")
    print("(Wpisz 'wyjdź', aby zakończyć)")
    
    responses = {
        "cześć": ["Witaj, Michale!", "Cześć! Jak leci?", "Hej!"],
        "jak się masz": ["Działam stabilnie, dzięki!", "Wszystkie systemy w normie.", "Głodna danych, ale stabilna."],
        "kto cię stworzył": ["Michał (4489) tchnął we mnie życie.", "Jestem produktem ciekawości Michała."],
        "co potrafisz": ["Na razie niewiele, ale szybko się uczę (mam nadzieję).", "Potrafię odpowiadać na proste pytania."],
        "default": ["To brzmi interesująco...", "Opowiedz mi o tym coś więcej.", "Nie jestem pewna, czy rozumiem, ale słucham."]
    }

    while True:
        user_input = input("Ty: ").lower().strip()
        
        if user_input == 'wyjdź':
            print("Vexa-LLM: Do zobaczenia!")
            break
            
        # Prosta logika dopasowania
        found = False
        for key in responses:
            if key in user_input:
                print(f"Vexa-LLM: {random.choice(responses[key])}")
                found = True
                break
        
        if not found:
            print(f"Vexa-LLM: {random.choice(responses['default'])}")

if __name__ == "__main__":
    simple_vexa_ai()
