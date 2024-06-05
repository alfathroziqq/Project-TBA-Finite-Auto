from flask import Flask, render_template, request
from graphviz import Digraph

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index4.html')

@app.route('/submit4', methods=['POST'])
def submit():
    dfa1 = {}
    dfa1['states'] = request.form['states1'].split()
    dfa1['input_symbols'] = request.form['symbol1'].split()
    dfa1['initial_state'] = request.form['initialState1']
    dfa1['final_states'] = request.form['finalStates1'].split()
    dfa1['transitions'] = {}
    for state in dfa1['states']:
        dfa1['transitions'][state] = {}
        for symbol in dfa1['input_symbols']:
            next_state = request.form.get(f'transitions1_{state}_{symbol}')
            dfa1['transitions'][state][symbol] = next_state
    
    dfa2 = {}
    dfa2['states'] = request.form['states2'].split()
    dfa2['input_symbols'] = request.form['symbol2'].split()
    dfa2['initial_state'] = request.form['initialState2']
    dfa2['final_states'] = request.form['finalStates2'].split()
    dfa2['transitions'] = {}
    for state in dfa2['states']:
        dfa2['transitions'][state] = {}
        for symbol in dfa2['input_symbols']:
            next_state = request.form.get(f'transitions2_{state}_{symbol}')
            dfa2['transitions'][state][symbol] = next_state

    graph1_dfano4 = visualize_dfano4(dfa1)
    graph2_dfano4 = visualize_dfano4(dfa2)

    result = equivalent(dfa1, dfa2)

    if result:
        result_message = "Kedua DFA Ekuivalen"
    else:
        result_message = "Kedua DFA Tidak Ekuivalen"

    return render_template('result4.html', result=result_message, 
                           graph1_dfano4=graph1_dfano4, graph2_dfano4=graph2_dfano4)

def visualize_dfano4(dfa):
    dot = Digraph()
    dot.attr(rankdir='LR')

    # Tambahkan node
    for state in dfa['states']:
        if state in dfa['final_states']:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state)

    # Tambahkan transisi
    for start_state, transitions in dfa['transitions'].items():
        for symbol, next_state in transitions.items():
            dot.edge(start_state, next_state, label=symbol)

    dot.attr('node', shape='none', label='start')
    dot.node('')
    dot.edge('', dfa['initial_state'])

    return dot.pipe(format='svg').decode('utf-8')

def get_next_state(current_state, symbol, transitions):
    return transitions.get(current_state, {}).get(symbol)

def are_states_equivalent(state1, state2, dfa1, dfa2, equivalent_table):
    return equivalent_table[state1][state2]

def equivalent(dfa1, dfa2):
    def initialize_equivalence_table(dfa1, dfa2):
        equivalent_table = {}
        for state1 in dfa1['states']:
            equivalent_table[state1] = {}
            for state2 in dfa2['states']:
                equivalent_table[state1][state2] = (state1 in dfa1['final_states']) == (state2 in dfa2['final_states'])
        return equivalent_table

    equivalent_table = initialize_equivalence_table(dfa1, dfa2)

    if not equivalent_table[dfa1['initial_state']][dfa2['initial_state']]:
        return False

    for state1 in dfa1['states']:
        for state2 in dfa2['states']:
            for symbol in dfa1['input_symbols']:
                next_state1 = get_next_state(state1, symbol, dfa1['transitions'])
                next_state2 = get_next_state(state2, symbol, dfa2['transitions'])
                if (next_state1 is None and next_state2 is not None) or (next_state1 is not None and next_state2 is None):
                    equivalent_table[state1][state2] = False

    while True:
        changed = False
        for state1 in dfa1['states']:
            for state2 in dfa2['states']:
                if not equivalent_table[state1][state2]:
                    continue
                for symbol in dfa1['input_symbols']:
                    next_state1 = get_next_state(state1, symbol, dfa1['transitions'])
                    next_state2 = get_next_state(state2, symbol, dfa2['transitions'])
                    if not are_states_equivalent(next_state1, next_state2, dfa1, dfa2, equivalent_table):
                        equivalent_table[state1][state2] = False
                        changed = True
                        break
            if changed:
                break
        if not changed:
            break

    for state1 in dfa1['states']:
        for state2 in dfa2['states']:
            if are_states_equivalent(state1, state2, dfa1, dfa2, equivalent_table):
                for symbol in dfa1['input_symbols']:
                    next_state1 = get_next_state(state1, symbol, dfa1['transitions'])
                    next_state2 = get_next_state(state2, symbol, dfa2['transitions'])
                    if not are_states_equivalent(next_state1, next_state2, dfa1, dfa2, equivalent_table):
                        return False
            else:
                if state1 in dfa1['final_states'] != state2 in dfa2['final_states']:
                    return False
    return True

if __name__ == "__main__":
    app.run(debug=True)