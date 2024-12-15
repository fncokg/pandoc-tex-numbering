import logging
import re

from panflute import *
from pylatexenc.latexwalker import LatexWalker,LatexEnvironmentNode,LatexMacroNode

logger = logging.getLogger('pandoc-tex-numbering')
hdlr = logging.FileHandler('pandoc-tex-numbering.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def prepare(doc):
    doc.pandoc_tex_numbering = {}
    doc.pandoc_tex_numbering["num_fig"] = doc.get_metadata("number-figures", True)
    doc.pandoc_tex_numbering["num_tab"] = doc.get_metadata("number-tables", True)
    doc.pandoc_tex_numbering["num_eq"] = doc.get_metadata("number-equations", True)
    doc.pandoc_tex_numbering["fig_pref"] = doc.get_metadata("figure-prefix", "Figure")
    doc.pandoc_tex_numbering["tab_pref"] = doc.get_metadata("table-prefix", "Table")
    doc.pandoc_tex_numbering["eq_reset_level"] = doc.get_metadata("equation-reset-level", 1)
    doc.pandoc_tex_numbering["ref_dict"] = {}
    doc.pandoc_tex_numbering["current_sec"] = [0]*10
    doc.pandoc_tex_numbering["current_eq"] = 0
    doc.pandoc_tex_numbering["current_fig"] = 0
    doc.pandoc_tex_numbering["current_tab"] = 0
    doc.pandoc_tex_numbering["multiline_envs"] = ["cases","align","aligned","alignedat","eqnarray","gather","gathered","multline","split"]
    doc.pandoc_tex_numbering["multiline_filter_pattern"] = re.compile(
        r"\\begin\{("+"|".join(doc.pandoc_tex_numbering["multiline_envs"])+")}"
    )
    doc.pandoc_tex_numbering["paras2wrap"] = []

def finalize(doc):
    for para,labels in doc.pandoc_tex_numbering["paras2wrap"]:
        if labels:
            parent = para.parent
            idx = parent.content.index(para)
            del parent.content[idx]
            div = Div(para,identifier=labels[0])
            for label in labels[1:]:
                div = Div(div,identifier=label)
            parent.content.insert(idx,div)
    del doc.pandoc_tex_numbering

def _current_section(doc,level=1):
    return ".".join(map(str,doc.pandoc_tex_numbering["current_sec"][:level]))

def _current_eq_numbering(doc,item="eq"):
    chp = _current_section(doc,level=doc.pandoc_tex_numbering["eq_reset_level"])
    eq = doc.pandoc_tex_numbering[f"current_{item}"]
    return f"{chp}.{eq}"


def _parse_multiline_environment(root_node,doc):
    labels = {}
    environment_body = ""
    # Multiple equations
    doc.pandoc_tex_numbering["current_eq"] += 1
    current_numbering = _current_eq_numbering(doc,"eq")
    for node in root_node.nodelist:
        if isinstance(node,LatexMacroNode):
            if node.macroname == "label":
                label = node.nodeargd.argnlist[0].nodelist[0].chars
                labels[label] = current_numbering
            if node.macroname == "\\":
                environment_body += f"\\qquad{{({current_numbering})}}"
                doc.pandoc_tex_numbering["current_eq"] += 1
                current_numbering = _current_eq_numbering(doc,"eq")
        environment_body += node.latex_verbatim()
    environment_body += f"\\qquad{{({current_numbering})}}"
    modified_math_str = f"\\begin{{{root_node.environmentname}}}{environment_body}\\end{{{root_node.environmentname}}}"
    return modified_math_str,labels

def _parse_plain_math(math_str:str,doc):
    labels = {}
    doc.pandoc_tex_numbering["current_eq"] += 1
    current_numbering = _current_eq_numbering(doc,"eq")
    modified_math_str = f"{math_str}\\qquad{{({current_numbering})}}"
    label_strings = re.findall(r"\\label\{(.*?)\}",math_str)
    if len(label_strings) >= 2:
        logger.warning(f"Multiple label_strings in one math block: {label_strings}")
    for label in label_strings:
        labels[label] = current_numbering
    return modified_math_str,labels

def parse_latex_math(math_str:str,doc):
    math_str = math_str.strip()
    # Add numbering to every line of the math block when and only when:
    # 1. The top level environment is a multiline environment
    # 2. The math block contains at least a label
    # Otherwise, add numbering to the whole math block

    # Fast check if it is a multiline environment
    if re.match(doc.pandoc_tex_numbering["multiline_filter_pattern"],math_str):
        walker = LatexWalker(math_str)
        nodelist,_,_ = walker.get_latex_nodes(pos=0)
        if len(nodelist) == 1:
            root_node = nodelist[0]
            if isinstance(root_node,LatexEnvironmentNode) and root_node.environmentname in doc.pandoc_tex_numbering["multiline_envs"] and not re.search(r"\\label",math_str) is None:
                return _parse_multiline_environment(root_node,doc)
    # Otherwise, add numbering to the whole math block
    return _parse_plain_math(math_str,doc)


def add_label_to_caption(numbering,label:str,caption_plain:Plain,prefix_str:str):
    url = f"#{label}" if label else ""
    label_items = [
        Str(prefix_str),
        Link(Str(numbering), url=url),
        Str(":"),
        Space()
    ]
    for item in label_items[::-1]:
        caption_plain.content.insert(0, item)

def find_labels_header(elem,doc):
    doc.pandoc_tex_numbering["current_sec"][elem.level-1] += 1
    for i in range(elem.level,10):
        doc.pandoc_tex_numbering["current_sec"][i] = 0
    if elem.level >= doc.pandoc_tex_numbering["eq_reset_level"]:
        doc.pandoc_tex_numbering["current_eq"] = 0
    for child in elem.content:
        if isinstance(child,Span) and "label" in child.attributes:
            label = child.attributes["label"]
            numbering = _current_section(doc,level=elem.level)
            doc.pandoc_tex_numbering["ref_dict"][label] = numbering

def find_labels_math(elem,doc):
    math_str = elem.text
    modified_math_str,labels = parse_latex_math(math_str,doc)
    elem.text = modified_math_str
    for label,numbering in labels.items():
        doc.pandoc_tex_numbering["ref_dict"][label] = numbering
    if labels:
        this_elem = elem
        while not isinstance(this_elem,Para):
            this_elem = this_elem.parent
            if isinstance(this_elem,Doc):
                logger.warning(f"Unexpected parent of math block: {this_elem}")
                break
        else:
            doc.pandoc_tex_numbering["paras2wrap"].append([this_elem,list(labels.keys())])

def find_labels_table(elem,doc):
    doc.pandoc_tex_numbering["current_tab"] += 1
    label = elem.parent.identifier
    numbering = _current_eq_numbering(doc,"tab")
    doc.pandoc_tex_numbering["ref_dict"][label] = numbering
    caption_plain: Plain = elem.caption.content[0]
    add_label_to_caption(numbering,label,caption_plain,doc.pandoc_tex_numbering["tab_pref"])

def find_labels_figure(elem,doc):
    doc.pandoc_tex_numbering["current_fig"] += 1
    label = elem.identifier
    numbering = _current_eq_numbering(doc,"fig")
    if label:
        doc.pandoc_tex_numbering["ref_dict"][label] = numbering
    caption_plain: Plain = elem.caption.content[0]
    add_label_to_caption(numbering,label,caption_plain,doc.pandoc_tex_numbering["fig_pref"])

def action_find_labels(elem, doc):
    # Find labels in headers, math blocks, figures and tables
    if isinstance(elem,Header):
        # We should always find labels in headers since we need the section numbering information
        find_labels_header(elem,doc)
    if isinstance(elem,Math) and elem.format == "DisplayMath" and doc.pandoc_tex_numbering["num_eq"]:
        find_labels_math(elem,doc)  
    if isinstance(elem,Figure) and doc.pandoc_tex_numbering["num_fig"]:
        find_labels_figure(elem,doc)
    if isinstance(elem,Table) and doc.pandoc_tex_numbering["num_tab"]:
        find_labels_table(elem,doc)

def action_replace_refs(elem, doc):
    if isinstance(elem, Link) and 'reference-type' in elem.attributes and elem.attributes['reference-type'] == 'ref':
        label = elem.attributes['reference']
        if label in doc.pandoc_tex_numbering["ref_dict"]:
            elem.content[0].text = doc.pandoc_tex_numbering["ref_dict"][label]
        else:
            logger.warning(f"Reference not found: {label}")

def main(doc=None):
    return run_filters([action_find_labels ,action_replace_refs], doc=doc,prepare=prepare, finalize=finalize)

if __name__ == '__main__':
    main()