"""
    Generate source code html with classed indicate student edit and corrections.
"""
import ast
import logging
import sys

import networkx as nx
import pandas as pd

import gen_edit_script
import map_asts
import muast
import simplify
import map_bytecode
import get_runtime_effects
import runtime_comparison
import tree_to_html

# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
html_correction_history = [] # correction edits
html_student_history = [] # student's edits
bugs = [] # correction to student's submission
changes = [] # next submission to last submission
edit_dist = []
change_dist = []

input_file = "S049howManyEggCartons"
code_history = pd.read_csv("./data/"+input_file+".csv")
student_code_history = code_history['student_solution']
correction_code_history = code_history['corrected']
descriptors = code_history['descriptors']
problem_unit_tests = [
    'howManyEggCartons(0) == 0',
    'howManyEggCartons(1) == 1',
    'howManyEggCartons(24) == 2',
    'howManyEggCartons(37) == 4',
]


def generate_html_code_history(student_code_history, correction_code_history):
    
    # remove submission with syntax errors
    student_code_history_without_syntax_error = []
    correct_code_history_without_syntax_error = []
    for i in range(len(student_code_history)):
        if 'Syntax error' not in descriptors[i]:
            student_code_history_without_syntax_error.append(student_code_history[i])
            correct_code_history_without_syntax_error.append(correction_code_history[i])
    student_code_history = student_code_history_without_syntax_error[:]
    correction_code_history = correct_code_history_without_syntax_error[:]
    
    for i in range(len(student_code_history)):
        print("========================= submission "+str(i)+" =========================")
        correction_edit, correction_fixes, edit_d = generate_one_html_code(student_code_history[i], correction_code_history[i], ' correction-node ')
        if (i == len(student_code_history)-1):
            student_edit, student_fixes, change_d = generate_one_html_code(student_code_history[i], student_code_history[i], ' student-node ')
        else:
            student_edit, student_fixes, change_d = generate_one_html_code(student_code_history[i], student_code_history[i+1], ' student-node ')
        
        html_correction_history.append(correction_edit)
        html_student_history.append(student_edit)
        bugs.append(correction_fixes)
        changes.append(student_fixes)
        edit_dist.append(edit_d)
        change_dist.append(change_d)
        
    df = pd.DataFrame(data={'correction_history':html_correction_history, 'student_history':html_student_history, 'bugs':bugs, 'changes':changes, 'edit_dist':edit_dist, 'change_dist':change_dist})
    df.to_csv("./out/"+input_file+".csv")
    
def generate_one_html_code(source_code, dest_code, default_class):
    source_tree, dest_tree, index_mapping = map_asts.get_trees_and_mapping(source_code, dest_code)
    edit_script = gen_edit_script.generate_edit_script(source_tree, dest_tree, index_mapping)
    edit_distance = len(edit_script.edits)
    all_fix_in_one_submission = generate_one_fix(edit_script)
    deps = edit_script.dependencies
    with open('./out/dependencies.dot', 'w') as dep_file:
        nx.drawing.nx_pydot.write_dot(deps, dep_file)

    html_source = tree_to_html.gen_annotated_html(source_tree, id_prefix='stu_', default_class=default_class, edit_script=edit_script)
    html_source = "<pre>"+html_source+"</pre>"
    html_source = html_source.replace("\n", "<br>")
    return html_source, all_fix_in_one_submission, edit_distance

def generate_one_fix(edit_script):
    
    all_fix = ""
    for fix in edit_script.dependent_blocks:
        print("fix")
        print(fix)
        all_fix += str(fix)
    #     fix_script = edit_script.filtered_copy(lambda edit: edit.short_string not in fix)
    #     tree_with_fix = fix_script.apply(source_tree)
    # print("fix_script after")
    # print(len(fix_script.edits))
    return all_fix
        
generate_html_code_history(student_code_history, correction_code_history)