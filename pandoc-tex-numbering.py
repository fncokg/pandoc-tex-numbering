import logging
import re
import json
from typing import Union

from panflute import *
from pylatexenc.latexwalker import LatexWalker,LatexEnvironmentNode,LatexMacroNode

logger = logging.getLogger('pandoc-tex-numbering')
hdlr = logging.FileHandler('pandoc-tex-numbering.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

MAX_LEVEL = 10

def to_string(elem):
    if isinstance(elem,Str):
        return elem.text
    elif isinstance(elem,Space):
        return " "
    elif isinstance(elem,(LineBreak,SoftBreak)):
        return "\n"
    elif isinstance(elem,ListContainer):
        return "".join([to_string(item) for item in elem])
    elif hasattr(elem,"content"):
        return "".join([to_string(item) for item in elem.content])
    else:
        return ""

def number_fields(numbers,max_levels,non_arabic_numbers=False):
    if non_arabic_numbers:
        from lang_num import language_functions
    fields = {}
    for i in range(1,len(numbers)+1):
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

        "data_export_path": doc.get_metadata("data-export-path", None),

        "fig_pref": doc.get_metadata("figure-prefix", "Figure"),
        "tab_pref": doc.get_metadata("table-prefix", "Table"),
        "eq_pref": doc.get_metadata("equation-prefix", "Equation"),
        "sec_pref": doc.get_metadata("section-prefix", "Section"),
        "pref_space": doc.get_metadata("prefix-space", True),

        "auto_labelling": doc.get_metadata("auto-labelling", True),

        "multiline_envs": doc.get_metadata("multiline-environments", "cases,align,aligned,gather,multline,flalign").split(","),
        "non_arabic_numbers": doc.get_metadata("non-arabic-numbers", False),

        # state variables
        "ref_dict": {},
        "current_sec": [0]*MAX_LEVEL,
        "current_eq": 0,
        "current_fig": 0,
        "current_tab": 0,
        "paras2wrap": [],
        "tabs2wrap": [],
    }

    # Initialize the section numbering formats
    section_formats_source = {}
    section_fromats_ref = {}
    ref_default_prefix = doc.pandoc_tex_numbering["sec_pref"]
    if doc.pandoc_tex_numbering["pref_space"]:
        ref_default_prefix += " "
    for i in range(1,MAX_LEVEL+1):
        default_format_source = ".".join([f"{{h{j}}}" for j in range(1,i+1)])
        default_format_ref = f"{ref_default_prefix} {default_format_source}"
        current_format_source = doc.get_metadata(f"section-format-source-{i}", default_format_source)
        current_format_ref = doc.get_metadata(f"section-format-ref-{i}", default_format_ref)
        section_formats_source[i] = lambda numbers,f=current_format_source: f.format(
            **number_fields(numbers,i,doc.pandoc_tex_numbering["non_arabic_numbers"])
        )
        section_fromats_ref[i] = lambda numbers,f=current_format_ref: f.format(
            **number_fields(numbers,i,doc.pandoc_tex_numbering["non_arabic_numbers"])
        )
    doc.pandoc_tex_numbering["sec_format_source"] = section_formats_source
    doc.pandoc_tex_numbering["sec_format_ref"] = section_fromats_ref
    
    # Prepare the multiline environment filter pattern for fast checking
    doc.pandoc_tex_numbering["multiline_filter_pattern"] = re.compile(
        r"\\begin\{("+"|".join(doc.pandoc_tex_numbering["multiline_envs"])+")}"
    )

def finalize(doc):
    for para,labels in doc.pandoc_tex_numbering["paras2wrap"]:
        if labels:
            try:
                parent = para.parent
                idx = parent.content.index(para)
                del parent.content[idx]
                div = Div(para,identifier=labels[0])
                for label in labels[1:]:
                    div = Div(div,identifier=label)
                parent.content.insert(idx,div)
            except Exception as e:
                logger.warning(f"Failed to add identifier to paragraph because of {e}. Pleas check: \n The paragraph: {para}. Parent of the paragraph: {parent}")
    for tab,label in doc.pandoc_tex_numbering["tabs2wrap"]:
        if label:
            parent = tab.parent
            idx = parent.content.index(tab)
            del parent.content[idx]
            div = Div(tab,identifier=label)
            parent.content.insert(idx,div)
    if doc.pandoc_tex_numbering["data_export_path"]:
        with open(doc.pandoc_tex_numbering["data_export_path"],"w") as f:
            json.dump(doc.pandoc_tex_numbering["ref_dict"],f,indent=2)
    del doc.pandoc_tex_numbering

def _current_section(doc,level=1):
    return ".".join(map(str,doc.pandoc_tex_numbering["current_sec"][:level]))

def _current_numbering(doc,item="eq"):
    reset_level = doc.pandoc_tex_numbering["num_reset_level"]
    num = doc.pandoc_tex_numbering[f"current_{item}"]
    if reset_level == 0:
        return str(num)
    else:
        sec = _current_section(doc,level=doc.pandoc_tex_numbering["num_reset_level"])
        return f"{sec}.{num}"


def _parse_multiline_environment(root_node,doc):
    labels = {}
    environment_body = ""
    # Multiple equations
    doc.pandoc_tex_numbering["current_eq"] += 1
    current_numbering = _current_numbering(doc,"eq")
    for node in root_node.nodelist:
        if isinstance(node,LatexMacroNode):
            if node.macroname == "label":
                label = node.nodeargd.argnlist[0].nodelist[0].chars
                labels[label] = current_numbering
            if node.macroname == "\\":
                environment_body += f"\\qquad{{({current_numbering})}}"
                doc.pandoc_tex_numbering["current_eq"] += 1
                current_numbering = _current_numbering(doc,"eq")
        environment_body += node.latex_verbatim()
    environment_body += f"\\qquad{{({current_numbering})}}"
    modified_math_str = f"\\begin{{{root_node.environmentname}}}{environment_body}\\end{{{root_node.environmentname}}}"
    return modified_math_str,labels

def _parse_plain_math(math_str:str,doc):
    labels = {}
    doc.pandoc_tex_numbering["current_eq"] += 1
    current_numbering = _current_numbering(doc,"eq")
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


def add_label_to_caption(numbering,label:str,elem:Union[Figure,Table],prefix_str:str,space:bool=True):
    url = f"#{label}" if label else ""
    label_items = [
        Str(prefix_str),
        Link(Str(numbering), url=url),
    ]
    has_caption = True
    if not elem.caption:
        elem.caption = Caption(Plain(Str("")),short_caption=ListContainer([Str("")]))
        has_caption = False
    if not elem.caption.content:
        elem.caption.content = [Plain(Str(""))]
        has_caption = False
    if has_caption:
        # If there's no caption text, we shouldnot add a colon
        label_items.extend([
            Str(":"),
            Space()
        ])
        
    if space:
        label_items.insert(1,Space())
    for item in label_items[::-1]:
        elem.caption.content[0].content.insert(0, item)


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
        elem.content.insert(0,Str(doc.pandoc_tex_numbering["sec_format_source"][elem.level](doc.pandoc_tex_numbering["current_sec"])))

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
    numbering = _current_numbering(doc,"tab")
    if isinstance(elem.parent,Div):
        label = elem.parent.identifier
        if not label and doc.pandoc_tex_numbering["auto_labelling"]:
            label = f"tab:{numbering}"
            elem.parent.identifier = label
    else:
        if doc.pandoc_tex_numbering["auto_labelling"]:
            label = f"tab:{numbering}"
            doc.pandoc_tex_numbering["tabs2wrap"].append([elem,label])
        else:
            label = ""
    
    add_label_to_caption(numbering,label,elem,doc.pandoc_tex_numbering["tab_pref"].capitalize(),doc.pandoc_tex_numbering["pref_space"])
    if label:
        doc.pandoc_tex_numbering["ref_dict"][label] = {
            "num": numbering,
            "type": "tab",
            "caption": to_string(elem.caption),
            "short_caption": to_string(elem.caption.short_caption)
        }

def find_labels_figure(elem,doc):
    doc.pandoc_tex_numbering["current_fig"] += 1
    label = elem.identifier
    numbering = _current_numbering(doc,"fig")
    if not label and doc.pandoc_tex_numbering["auto_labelling"]:
        label = f"fig:{numbering}"
        elem.identifier = label
    
    add_label_to_caption(numbering,label,elem,doc.pandoc_tex_numbering["fig_pref"].capitalize(),doc.pandoc_tex_numbering["pref_space"])
    if label:
        doc.pandoc_tex_numbering["ref_dict"][label] = {
            "num": numbering,
            "type": "fig",
            "caption": to_string(elem.caption),
            "short_caption": to_string(elem.caption.short_caption)
        }

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

def cleveref_numbering(numbering_info,doc,capitalize=False):
    label_type = numbering_info["type"]
    num = numbering_info["num"]
    if label_type == "sec":
        text = doc.pandoc_tex_numbering["sec_format_ref"][numbering_info["level"]](num.split("."))
    else:
        prefix = doc.pandoc_tex_numbering[f"{label_type}_pref"]
        if doc.pandoc_tex_numbering["pref_space"]:
            prefix += " "
        text = f"{prefix}{num}"
    if capitalize:
        text = text.capitalize()
    else:
        text = text.lower()
    return text

def action_replace_refs(elem, doc):
    if isinstance(elem, Link) and 'reference-type' in elem.attributes:
        labels = elem.attributes['reference'].split(",")
        if len(labels) == 1:
            label = labels[0]
            if label in doc.pandoc_tex_numbering["ref_dict"]:
                numbering_info = doc.pandoc_tex_numbering["ref_dict"][label]
                ref_type = elem.attributes['reference-type']
                if ref_type == 'ref':
                    elem.content[0].text = numbering_info["num"]
                elif ref_type == 'ref+label':
                    elem.content[0].text = cleveref_numbering(numbering_info,doc,capitalize=False)
                elif ref_type == 'ref+Label':
                    elem.content[0].text = cleveref_numbering(numbering_info,doc,capitalize=True)
                elif ref_type == 'eqref':
                    elem.content[0].text = f"({numbering_info['num']})"
                else:
                    logger.warning(f"Unknown reference-type: {elem.attributes['reference-type']}")
            else:
                logger.warning(f"Reference not found: {label}")
        else:
            logger.warning(f"Currently only support one label in reference: {labels}")

def main(doc=None):
    return run_filters([action_find_labels ,action_replace_refs], doc=doc,prepare=prepare, finalize=finalize)

if __name__ == '__main__':
    main()