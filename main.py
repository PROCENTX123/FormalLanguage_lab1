import sys

def parse_constructor(str_constructor):
    constructor = dict()
    arr_all_constructor = str_constructor.split('=')[1].split(',')
    for i in range(0, len(arr_all_constructor)):
        name_constructor = arr_all_constructor[i].split('(')[0]
        value_constructor = arr_all_constructor[i].split('(')[1].split(')')[0]
        constructor[name_constructor] = value_constructor
    return constructor

def parse_variables(str_variables):
    variables = set()
    arr_all_variables = str_variables.split('=')[1].split(',')
    for i in range(0, len(arr_all_variables)):
        variables.add(arr_all_variables[i])
    return variables

def parse_term(str_term):
    name_term = str_term[0]
    res = {name_term:[]}
    str_term = str_term[1:]
    if (str_term[0] == '('):
        __c = str_term[0]
        str_term = str_term[1:]
        while (__c != ')'):
            str_term, child = parse_term(str_term)
            res[name_term].append(child)
            __c = str_term[0]
            str_term = str_term[1:]
    return str_term, res

def get_variable_tree(tree, variables, constructor):
    variable_in_term = set()
    for key in tree:
        children = tree.get(key)
        for i in range(0, len(children)):
            for keys in tree.get(key)[i]:
                a = children[i]
                if keys in constructor:
                   dop_var = get_variable_tree(a, variables, constructor)
                   for j in dop_var:
                       variable_in_term.add(j)
                if keys in variables:
                    variable_in_term.add(keys)
    return variable_in_term

def make_multieq(term1, term2, var_in_term_all):
    arr_term = []
    arr_term_with_0 = []
    arr_multieq = []
    var_in_term_all.insert(0, 'x0')
    arr_term.append(term1)
    arr_term.append(term2)
    for i in range(0, len(var_in_term_all) - 1):
        arr_term_with_0.append([])
    arr_term_with_0.insert(0, arr_term)
    for i in range(0, len(var_in_term_all)):
        kort = ([var_in_term_all[i]], arr_term_with_0[i])
        arr_multieq.append(kort)
    return arr_multieq

def dec(uniq_eq, variables):
    is_variable = None
    all_constructor = True
    buf = []
    name_root = next(uniq_eq[0].__iter__())
    for i in range (0, len(uniq_eq)):
        for key in uniq_eq[i]:
            if key in variables:
                is_variable = key
            else:
                all_constructor &= name_root == key
    if is_variable:
        mutieq = ([], [])
        for i in range (0, len(uniq_eq)):
            for key in uniq_eq[i]:
                if key in variables:
                    mutieq[0].append(key)
                else:
                    mutieq[1].append(uniq_eq[i])
        return is_variable, [mutieq]
    elif all_constructor:
        common = {name_root: []}
        border = []
        for i in range(0, len(uniq_eq[0][name_root])):
            for j in range(len(uniq_eq)):
                buf.append(uniq_eq[j][name_root][i])
            new_common, new_border = dec(buf, variables)
            if new_common is None:
                return None, None
            buf = []
            common[name_root].append(new_common)
            border = merge(border, new_border)
        return common, border
    else:
        return None, None


def merge(border, new_border):
    for new_multeq in new_border:
        for multeq in border:
            if len(set(new_multeq[0]) & set(multeq[0])):
                tmp = new_multeq[0].copy()
                new_multeq[0].clear()
                new_multeq[0].extend(list(set(tmp) | set(multeq[0])))
                for term in multeq[1]:
                    if term not in new_multeq[1]:
                        new_multeq[1].append(term)
        border = list(filter(lambda x: len(set(new_multeq[0]) & set(x[0])) == 0, border))
        border.append(new_multeq)
    return border


def find_uniq_equ(arr_mulieq, variables, constructor):
    for array_l, array_r in arr_mulieq:
        unify = True
        for array_lhs, array_rhs in arr_mulieq:
            if array_lhs == array_l or len(array_rhs) == 0:
                continue
            array_variable_rhs = list(map(lambda x : get_variable_tree(x, variables, constructor), array_rhs))
            array_variable_rhs = set().union(*array_variable_rhs)
            unify &= len(set(array_l) & array_variable_rhs) == 0
            if not unify:
                break
        if unify:
            return array_l, array_r
    return None

#algorythm
def unify(term1, term2, variables, constructor):
    res = []

    # создание списка переменных с обоих термов
    var_in_term1 = get_variable_tree(term1, variables, constructor)
    var_in_term2 = get_variable_tree(term2, variables, constructor)
    var_in_term_all = list(set().union(var_in_term1, var_in_term2))

    # создание системы мультиуравнений
    arr_multieq = make_multieq(term1, term2, var_in_term_all)

    while len(arr_multieq) != 0:
        a = find_uniq_equ(arr_multieq, variables, constructor)
        if a is None:
            print("ERROR")
            sys.exit(0)
        if len(a[1]) == 0:
            res.append((a[0], []))
            arr_multieq.remove(a)
        else:
            common, border = dec(a[1], variables)
            if common is None:
                print("ERROR")
                sys.exit(0)
            res.append((a[0], common))
            arr_multieq.remove(a)
            arr_multieq = merge(arr_multieq, border)
    return res


if __name__ == "__main__":
    data = list()
    var_in_term_all = set()
    for line in sys.stdin:
        line = line.replace(' ', '').replace('\n', '').replace('\t', '')
        if len(line) != 0:
            data.append(line)
        if len(data) == 4:
            break
    term_str_first_term = data[2].split('=')[1]
    term_str_second_term = data[3].split('=')[1]

    # парсинг данных
    constructor = parse_constructor(data[0])
    variables = parse_variables(data[1])
    _, term1 = parse_term(term_str_first_term)
    _, term2 = parse_term(term_str_second_term)


    print(unify(term1, term2, variables, constructor))


# test1
# constructor = f(4), g(2), h(2), p(0), o(0)
# variables = a, b, v, s, m
# term1 = f(a, g(b, v), b, p)
# term2 = f(g(h(o, m), b), a, h(o, s), s)

#test2
# constructor = f(3)
# variables = a, b, c
# term1 = f(a, b, c)
# term2 = f(b, a, c)

