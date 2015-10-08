import json


def verify_ops(con_ops):
    # FIXME
    # There are a few conditions I don't check yet
    # For instance, you can do accumulator operations for free
    # But loading something into the accumulator while doing such an operation
    # should fail.
    # Similarly, writing to or reading from a register doing I/O should fail.
    write_ops = set(filter(lambda op: op == ('M(MAR)', 'MDR'), con_ops))
    read_ops = set(filter(lambda op: op == ('MDR', 'M(MAR)'), con_ops))
    bus_ops = (set(con_ops) - write_ops) - read_ops
    # Check that writing isn't happening at the same time as reading
    assert len(write_ops) + len(read_ops) < 2
    # Check that the right hand side of all non-IO operations is the same,
    # That is we aren't double dipping on the internal data bus.
    if len(bus_ops) > 0:
        rights = map(lambda op: op[1], bus_ops)
        first = rights.pop()
        assert all(map(lambda right: first == right, rights))
    return True

def do_op(op):
    left, right = op
    print op, memory, registers
    if right == 'M(MAR)':
        registers[left] = memory[str(registers['MAR'])]
    elif left == 'M(MAR)':
        memory[str(registers['MAR'])] = registers[right]
    elif right[-2:] == '+1':
        registers[left] = int(registers[right[:-2]]) + 1
    elif right[-2:] == '-1':
        registers[left] = int(registers[right[:-2]]) - 1
    elif right not in registers.keys():
        registers[left] = int(right)
    else:
        registers[left] = registers[right]


if __name__ == '__main__':
    # FIXME: Adopt functional style where environments are passed between
    # functions.
    registers = {
        'AC': 0,
        'MDR': 0,
        'MAR': 0,
        'TEMP': 0,
        'IR': 0,
        'PC': 0
    }
    memory = json.load(open('initial_state.json'))
    registers['MDR'] = memory['MDR']
    registers['MAR'] = memory['MAR']
    del memory['MDR']
    del memory['MAR']

    with open('microops.txt', 'r') as f:
        ops = f.readlines()

    for op in ops:
        op = op.replace(' ', '').replace('\n', '')
        if op == '':
            continue
        con_ops = op.split(',')
        con_ops = map(lambda x: tuple(x.split('<-')), con_ops)
        verify_ops(con_ops)
        map(do_op, con_ops)

    # FIXME: Refactor into own function.
    desired_memory = json.load(open('desired_memory.json'))
    desired_state = json.load(open('desired_state.json'))

    for key, value in desired_memory.items():
        print memory[key], value, key
        assert memory[key] == value
    for key, value in desired_state.items():
        print registers[key], value, key
        assert registers[key] == value
