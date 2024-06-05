def state_to_string(state):
    return "".join(sorted(state))

# Inisialisasi variabel dfa_final_states sebagai set
dfa_final_states = set()

# Fungsi epsilon_closure()
def epsilon_closure(states):
    closure = set()
    stack = list(states)
    while stack:
        current_state = stack.pop()
        closure.add(current_state)
        epsilon_transitions = k[s.index(current_state)][-1]  # Transisi epsilon
        for state in epsilon_transitions:
            if state not in closure:
                stack.append(state)
                closure.add(state)
    return closure

# Fungsi move()
def move(states, symbol):
    next_states = set()
    for state in states:
        transitions = k[s.index(state)][t.index(symbol)] 
        next_states.update(transitions)
    epsilon_transitions = epsilon_closure(next_states)
    next_states.update(epsilon_transitions)
    return next_states

# Fungsi get_dfa_states()
def get_dfa_states(nfa_states):
    global dfa_final_states
    dfa_states = []
    queue = [nfa_states]
    while queue:
        current_states = queue.pop(0)
        dfa_states.append(current_states)
        # menambahkan semua final state ke dalam set dfa_final_states
        for state in current_states:
            if state in last:
                dfa_final_states.add(state_to_string(current_states))
                break
        for symbol in t:
            next_states = move(current_states, symbol)
            if next_states not in dfa_states:
                queue.append(next_states)
                dfa_states.append(next_states)
    return dfa_states

# Input pengguna
x = int(input("Enter the number of states: "))
s = [input("Enter the states: ") for i in range(x)]
y = int(input("Enter the number of alphabets: "))
t = [input("Enter the alphabet: ") for j in range(y)]
last = input("Final States (separated by space): ")

# Matriks k yang berisi transisi antar state NFA
k = [[set() for j in range(len(t) + 1)] for i in range(len(s))]
for i in range(len(s)):
    for j in range(len(t) + 1):
        if j == len(t):  # Transisi epsilon
            k[i][j] = set(input('from ' + s[i] + ' if ε go (separated by space): ').split())
        else:
            k[i][j] = set(input('from ' + s[i] + ' if ' + t[j] + ' go (separated by space): ').split())

# Mendapatkan state DFA
dfa_states = get_dfa_states(epsilon_closure({s[0]}))

# DFA Transition Table
dfa_transitions = {}
for state in dfa_states:
    dfa_transitions[state_to_string(state)] = {}
    for symbol in t:
        next_states = move(state, symbol)
        next_state_string = state_to_string(next_states)
        dfa_transitions[state_to_string(state)][symbol] = next_state_string

# Menampilkan tabel transisi NFA
print("\nNFA Transition Table:")
print("States\t", end="")
for symbol in t + ['ε']:
    print(symbol, "\t", end="")
print()
for i, state in enumerate(s):
    print(state, "\t", end="")
    for j in range(len(t) + 1):
        transitions = k[i][j]
        sorted_transitions = sorted(transitions)  # Sort the transitions for consistent order
        print("".join(sorted_transitions) if sorted_transitions else "-", "\t", end="")
    print()

# Menampilkan tabel transisi DFA
print("\nDFA Transition Table:")
print("States\t", end="")
for symbol in t:
    print(symbol, "\t", end="")
print()
for state, transitions in dfa_transitions.items():
    print(state, "\t", end="")
    for symbol in t:
        next_state_string = transitions.get(symbol, None)
        print(next_state_string, "\t", end="")
    print()

# Menampilkan final states DFA
print("\nFinal states of the DFA are : ", ", ".join(dfa_final_states))