import ast
import logging
import sys

import networkx as nx

import gen_edit_script
import map_asts
import muast
import simplify
import map_bytecode
import get_runtime_effects
import runtime_comparison
import tree_to_html

# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

student_code = '''
def kthDigit(x, k):
    kthDigLeft = x%(10**(k+1))
    kthDigRight = kthDigLeft//(10**k)
    return kthDigRight
'''

fixed_code1 = '''
def kthDigit(x, k):
    kthDigLeft = x%(10**(k))
    kthDigRight = kthDigLeft//(10**(k-1))
    return kthDigRight
'''

fixed_code2 = '''
def kthDigit(x, k):
    kthDigLeft = x%(10**(k))
    y = kthDigLeft//(10**(k-1))
    return y
'''

kth_digit_unit_tests = [
    "kthDigit(4,1)==4",
    "kthDigit(123,2)==2",
    "kthDigit(5003,3)==0",
    "kthDigit(98,1)==8",
]

### Sample 1: transform python code to MutableAst object; print it out, output AST to file
code_tree = muast.MutableAst(ast.parse(student_code))
print('student code (from AST):')
print(code_tree)  # str conversion attempts to convert AST back to code
code_tree.write_dot_file('sample', './out/sample.dot')  # draw AST of code in graphviz format (.dot file)

### Sample 2: generate mapping and edit script between pairs of code (student code and each of two fixed versions)
for fixed_code in [fixed_code1, fixed_code2]:
    print()
    print()
    # get MutableAst objects and mapping between them:
    source_tree, dest_tree, index_mapping = map_asts.get_trees_and_mapping(student_code, fixed_code)
    print('fixed version of code:')
    print(dest_tree)
    # generate edit script and additional metadata which is needed to use the edit script.
    edit_script = gen_edit_script.generate_edit_script(source_tree, dest_tree, index_mapping)

    print('The edit distance is:', edit_script.edit_distance)

    # print out edit script
    print('Edits in edit script:')
    for e in edit_script.edits:
        print(e)

    # Draw the dependency graph between edits in the edit script
    # (usually not actually something you need to think about -
    #  this is data that's used by the simplification step to know which edits belong "together")
    deps = edit_script.dependencies
    with open('./out/dependencies.dot', 'w') as dep_file:
        nx.drawing.nx_pydot.write_dot(deps, dep_file)
    
    print('code after applying edit script:')
    print(edit_script.apply(source_tree))

    simplified = simplify.simplify_edit_script(source_tree, kth_digit_unit_tests, edit_script)
    print('Code after simplifying:')
    print(simplified.apply(source_tree))
    
    source_tree.generate_xml_file_for_gumtree("./out/sourceTree.html")
    dest_tree.generate_xml_file_for_gumtree("./out/destTree.html")
    print("html source")
    print(tree_to_html.gen_annotated_html(source_tree, id_prefix='source_', edit_script=simplified))
    print("html dest")
    print(tree_to_html.gen_annotated_html(dest_tree, id_prefix='dest_', edit_script=simplified))


### Sample 3: generate (and use) mapping from bytecode op ids to AST nodes that (probably) produced them

# student_tree = muast.MutableAst(ast.parse(student_code))
# tree_ops = map_bytecode.FlatOpsList(student_tree)
# tree_index_to_node = student_tree.gen_index_to_node()

# ops_to_nodes = map_bytecode.gen_op_to_node_mapping(student_tree)

# for op in tree_ops:
#     print(op.id, op, ops_to_nodes[op.id])
#     if ops_to_nodes[op.id]:
#         print(tree_index_to_node[ops_to_nodes[op.id]].name)  # name property of the node
#         print(tree_index_to_node[ops_to_nodes[op.id]])  # node converted to string (usually code)


# ### Sample 4: instrument student code and run it against a unit test
# ### to get the sequence of bytecode ops that were executed, and the values they produced.

# # Run code and ONE of the unit tests to get the runtime effect:
# run_result: get_runtime_effects.TracedRunResult = get_runtime_effects.run_test(student_code, kth_digit_unit_tests[1])

# # parse and print out result:
# print('Completion status of running code (or error):', run_result.run_outcome)
# print('Did unit test pass?', run_result.eval_result)
# print()
# for traced_op in run_result.ops_list:
#     print(f'Executed op {traced_op.op_id}, pushed values: {traced_op.pushed_values}')

#     # TODO: helper function to go from op_id to human readable bytecode representation

#     # we can use the bytecode-to-node mapping from sample 3 to look up how each executed op_id is represented in code
#     op_node_id = ops_to_nodes[traced_op.op_id]
#     if op_node_id:
#         # then look up node by id, if it exists
#         # the executed op may not be mapped to a tree node, e.g. if it's a default return which happens in every program
#         op_node_representation = tree_index_to_node[op_node_id].to_compileable_str()
#         print('code corresponding to executed op:')
#         print(op_node_representation)
#     print()

# ### Sample 5: compare outcome of running buggy code vs. corrected code with a given unit test

# # NOTE: RuntimeComparison depends on the assumption that the two ASTs being compared are derived from each other,
# # in the sense that nodes in the ASTs that would be mapped to each other in an AST mapping already have the same IDs.
# # in the big pipeline of generating and explaining fixes, this is true because the ASTs being compared are
# # (1) the AST of the original student code and (2) the corrected version as generated by applying an edit script to
# # the student code.
# # So we re-create something similar here.

# corrected_tree = simplified.apply(source_tree)

# comp = runtime_comparison.RuntimeComparison(source_tree, corrected_tree, kth_digit_unit_tests[0])
# print(comp)


# ### Sample 6: generate correction made up of several partial fixes
# # and describe improvements resulting from each partial fix


# # we start from scratch with another submission from the same student as in student_code above

# buggy_code = '''
# def kthDigit(x, k):
#     TrimLeft = x%(10**k)
#     TrimRight = TrimLeft//(10**k)
#     return kthDigRight
# '''

# other_student_correct_code = '''
# def kthDigit(x, k):
#     answer = x % 10 ** k
#     new = answer // 10 ** (k - 1)
#     return new
# '''

# source_tree, dest_tree, index_mapping = map_asts.get_trees_and_mapping(buggy_code, other_student_correct_code)
# edit_script = gen_edit_script.generate_edit_script(source_tree, dest_tree, index_mapping)
# simplified = simplify.simplify_edit_script(source_tree, kth_digit_unit_tests, edit_script)

# # perform runtime analysis of applying all fixes together:
# totally_corrected_tree = simplified.apply(source_tree)
# student_to_correct_comparison = runtime_comparison.RuntimeComparison(source_tree, totally_corrected_tree,
#                                                                     kth_digit_unit_tests[0])
# print('Initial student code:')
# print(source_tree)
# print()

# # Apply each "dependent block" (block of edits that constitute one fix) separately:
# for fix in simplified.dependent_blocks:
#     fix_script = simplified.filtered_copy(lambda edit: edit.short_string not in fix)
#     tree_with_fix = fix_script.apply(source_tree)
#     partial_fix_to_correct_comparison = runtime_comparison.RuntimeComparison(tree_with_fix, totally_corrected_tree,
#                                                                             kth_digit_unit_tests[0])
#     print('Student code with partial fix applied:')
#     print(tree_with_fix)
#     print(student_to_correct_comparison.describe_improvement_or_regression(partial_fix_to_correct_comparison))


