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

MAX_LEVEL = 10

def number_fields(numbers,max_levels,non_arabic_numbers=False):
    if non_arabic_numbers:
        from lang_num import language_functions
    fields = {}
    for i in range(1,max_levels+1):
        fields[f"h{i}"] = str(numbers[i-1])
        if non_arabic_numbers:
            for language,func in language_functions.items():
                fields[f"h{i}_{language}"] = func(numbers[i-1])
    return fields

def prepare(doc):
    # These are global variables that will be used in the action functions, and will be destroyed after the finalization
    doc.pandoc_tex_numbering = {
        # settings
        "num_fig": doc.get_metadata("number-figures", True),
        "num_tab": doc.get_metadata("number-tables", True),
        "num_eq": doc.get_metadata("number-equations", True),
        "num_sec": doc.get_metadata("number-sections", True),
        "num_reset_level": int(doc.get_metadata("number-reset-level", 1)),

        "fig_pref": doc.get_metadata("figure-prefix", "Figure"),
        "tab_pref": doc.get_metadata("table-prefix", "Table"),
        "eq_pref": doc.get_metadata("equation-prefix", "Equation"),
        "sec_pref": doc.get_metadata("section-prefix", "Section"),
        "pref_space":doc.get_metadata("prefix-space", True),

        "multiline_envs": doc.get_metadata("multiline-environments", "cases,align,aligned,gather,multline,flalign").split(","),
        "non_arabic_numbers": doc.get_metadata("non-arabic-numbers", False),

        # state variables
        "ref_dict": {},
        "current_sec": [0]*MAX_LEVEL,
        "current_eq": 0,
        "current_fig": 0,
        "current_tab": 0,
        "paras2wrap": []
    }

    # Initialize the section numbering formats
    section_formats = {}
    for i in range(1,MAX_LEVEL+1):
        default_format = ".".join([f"{{h{j}}}" for j in range(1,i+1)])
        current_format = doc.get_metadata(f"section-format-{i}", default_format)
        section_formats[i] = lambda numbers,f=current_format: f.format(
            **number_fields(numbers,i,doc.pandoc_tex_numbering["non_arabic_numbers"])
        )
    doc.pandoc_tex_numbering["sec_num_formats"] = section_formats
    
    # Prepare the multiline environment filter pattern for fast checking
    doc.pandoc_tex_numbering["multiline_filter_pattern"] = re.compile(
        r"\\begin\{("+"|".join(doc.pandoc_tex_numbering["multiline_envs"])+")}"
    )

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
    chp = _current_section(doc,level=doc.pandoc_tex_numbering["num_reset_level"])
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
            if isinstance(root_node,LatexEnvironmentNode) and root_node.environmentname in doc.pandoc_tex_numbering["multiline_envs"]:
                return _parse_multiline_environment(root_node,doc)
    # Otherwise, add numbering to the whole math block
    return _parse_plain_math(math_str,doc)


def add_label_to_caption(numbering,label:str,caption_plain:Plain,prefix_str:str,space:bool=True):
    url = f"#{label}" if label else ""
    label_items = [
        Str(prefix_str),
        Link(Str(numbering), url=url),
        Str(":"),
        Space()
    ]
    if space:
        label_items.insert(1,Space())
    for item in label_items[::-1]:
        caption_plain.content.insert(0, item)

def find_labels_header(elem,doc):
    doc.pandoc_tex_numbering["current_sec"][elem.level-1] += 1
    for i in range(elem.level,10):
        doc.pandoc_tex_numbering["current_sec"][i] = 0
    if elem.level >= doc.pandoc_tex_numbering["num_reset_level"]:
        doc.pandoc_tex_numbering["current_eq"] = 0
    for child in elem.content:
        if isinstance(child,Span) and "label" in child.attributes:
            label = child.attributes["label"]
            numbering = _current_section(doc,level=elem.level)
            doc.pandoc_tex_numbering["ref_dict"][label] = {
                "num": numbering,
                "level": elem.level,
                "type": "sec"
            }
    if doc.pandoc_tex_numbering["num_sec"]:
        elem.content.insert(0,Space())
        elem.content.insert(0,Str(doc.pandoc_tex_numbering["sec_num_formats"][elem.level](doc.pandoc_tex_numbering["current_sec"])))

def find_labels_math(elem,doc):
    math_str = elem.text
    modified_math_str,labels = parse_latex_math(math_str,doc)
    elem.text = modified_math_str
    for label,numbering in labels.items():
        doc.pandoc_tex_numbering["ref_dict"][label] = {
            "num": numbering,
            "type": "eq"
        }
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
    # The label of a table will be added to a div element wrapping the table, if any. And if there is not, the div element will be not created.
    if isinstance(elem.parent,Div):
        label = elem.parent.identifier
    else:
        label = ""
    numbering = _current_eq_numbering(doc,"tab")
    if label:
        doc.pandoc_tex_numbering["ref_dict"][label] = {
            "num": numbering,
            "type": "tab"
        }
    caption_plain: Plain = elem.caption.content[0]
    add_label_to_caption(numbering,label,caption_plain,doc.pandoc_tex_numbering["tab_pref"].capitalize(),doc.pandoc_tex_numbering["pref_space"])

def find_labels_figure(elem,doc):
    doc.pandoc_tex_numbering["current_fig"] += 1
    label = elem.identifier
    numbering = _current_eq_numbering(doc,"fig")
    if label:
        doc.pandoc_tex_numbering["ref_dict"][label] = {
            "num": numbering,
            "type": "fig"
        }
    caption_plain: Plain = elem.caption.content[0]
    add_label_to_caption(numbering,label,caption_plain,doc.pandoc_tex_numbering["fig_pref"].capitalize(),doc.pandoc_tex_numbering["pref_space"])

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
    if isinstance(elem, Link) and 'reference-type' in elem.attributes:
        label = elem.attributes['reference']
        if label in doc.pandoc_tex_numbering["ref_dict"]:
            numbering_info = doc.pandoc_tex_numbering["ref_dict"][label]
            if elem.attributes['reference-type'] == 'ref':
                elem.content[0].text = numbering_info["num"]
            elif elem.attributes['reference-type'] == 'ref+label':
                label_type = numbering_info["type"]
                prefix = doc.pandoc_tex_numbering[f"{label_type}_pref"].lower()
                text = f"{prefix} {numbering_info['num']}" if doc.pandoc_tex_numbering["pref_space"] else f"{prefix}{numbering_info['num']}"
                elem.content[0].text = text
            elif elem.attributes['reference-type'] == 'ref+Label':
                label_type = numbering_info["type"]
                prefix = doc.pandoc_tex_numbering[f"{label_type}_pref"].capitalize()
                text = f"{prefix} {numbering_info['num']}" if doc.pandoc_tex_numbering["pref_space"] else f"{prefix}{numbering_info['num']}"
                elem.content[0].text = text
            else:
                logger.warning(f"Unknown reference-type: {elem.attributes['reference-type']}")
        else:
            logger.warning(f"Reference not found: {label}")

def main(doc=None):
    return run_filters([action_find_labels ,action_replace_refs], doc=doc,prepare=prepare, finalize=finalize)

if __name__ == '__main__':
    main()