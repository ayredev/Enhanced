lines = open('ast_nodes.py').readlines()
with open('ast_nodes.py', 'w') as f:
    for line in lines:
        if 'super().__init__("' in line:
            f.write(line.split('super().__init__("')[0] + 'super().__init__()\n')
        else:
            f.write(line)
