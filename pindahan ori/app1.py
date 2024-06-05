from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Ambil data input dari formulir
        states = set(request.form['states'].split(","))
        alphabet = set(request.form['alphabet'].split(","))
        transitions = {}
        transitions_input = request.form.getlist('transitions')  # Ambil semua transisi dari formulir
        for transition in transitions_input:
            source, symbol, destination = transition.split(",")
            transitions[(symbol.strip(), source.strip())] = transitions.get((symbol.strip(), source.strip()), set()) | {destination.strip()}
        start_state = request.form['start_state']
        accept_states = set(request.form['accept_states'].split(","))
        # Buat objek NFA dari data input
        nfa = NFA(states, alphabet, transitions, start_state, accept_states)
        # Konversi NFA menjadi DFA
        dfa = nfa.nfa_to_dfa()
        # Tampilkan tabel transisi DFA
        dfa_table = dfa.display_transition_table()
        return render_template('index1.html', dfa_table=dfa_table)
    return render_template('index1.html', dfa_table=None)

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            if ('', state) in self.transitions:
                for next_state in self.transitions[('', state)]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return frozenset(closure)

    def move(self, states, symbol):
        reachable_states = set()
        for state in states:
            if (symbol, state) in self.transitions:
                reachable_states.update(self.transitions[(symbol, state)])
        return frozenset(reachable_states)

    def nfa_to_dfa(self):
        dfa_states = set()
        dfa_transitions = {}
        dfa_start_state = self.epsilon_closure({self.start_state})
        dfa_accept_states = set()
        unmarked_states = [dfa_start_state]

        while unmarked_states:
            current_state_set = unmarked_states.pop(0)
            dfa_states.add(current_state_set)

            for symbol in self.alphabet:
                next_state = self.move(current_state_set, symbol)
                epsilon_closure_next = self.epsilon_closure(next_state)

                if epsilon_closure_next:
                    dfa_transitions[(current_state_set, symbol)] = epsilon_closure_next

                    if epsilon_closure_next not in dfa_states:
                        unmarked_states.append(epsilon_closure_next)

            if any(state in self.accept_states for state in current_state_set):
                dfa_accept_states.add(current_state_set)

        return DFA(dfa_states, self.alphabet, dfa_transitions, dfa_start_state, dfa_accept_states)

class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def display_transition_table(self):
        dfa_table = []
        dfa_table.append("Tabel Transisi DFA:")
        dfa_table.append("---------------------------------------------------------------")
        dfa_table.append("|   Keadaan   |  " + "  |  ".join(self.alphabet) + "  |")
        dfa_table.append("---------------------------------------------------------------")
        max_state_length = max(len(str(state)) for state in self.states)  # Panjang maksimum dari nama keadaan
        for state in self.states:
            row = "|"
            if state == self.start_state:
                row += " -> "
            elif state in self.accept_states:
                row += "  * "
            else:
                row += "    "
            row += f" {state} ".ljust(max_state_length + 6) + "|"
            for symbol in self.alphabet:
                next_state = self.transitions.get((state, symbol), set())
                # Ubah set menjadi string untuk menghindari frozenset
                next_state_str = ', '.join(next_state)
                row += f" {next_state_str} ".ljust(len(symbol) + 6) + "|"
            dfa_table.append(row)
        dfa_table.append("---------------------------------------------------------------")
        return '\n'.join(dfa_table)


if __name__ == '__main__':
    app.run(debug=True)
