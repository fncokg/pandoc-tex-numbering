"""
Module for creating a list of items in a Word document.

Similar functionality can be achieved by adding files such as `html_list.py` to this filter.
"""
from .oxml import *
from panflute import RawBlock

def docx_list_heading(title,style_name="TOCHeading",east_asian_lang=None):
    # Create a paragraph with the specified style
    par = Paragraph()
    par_prop = ParagraphProperty()
    par_prop.set_style(style_name)
    if east_asian_lang:
        par_prop.set_eastAsian(east_asian_lang)
    par.set_property(par_prop)
    run = par.add_run()
    run.add_text(title)

    return RawBlock(par.to_string(),format="openxml")

def docx_list_body(items,leader_type="middleDot",style_name="TOC1",east_asian_lang=None):
    # Create a paragraph with the specified style and tabs
    par = Paragraph()
    par_prop = ParagraphProperty()
    par_prop.set_style(style_name)
    if east_asian_lang:
        par_prop.set_eastAsian(east_asian_lang)
    par.set_property(par_prop)

    # Add the items to the paragraph
    for caption,identifier in items:
        par.add_hyperlink(identifier,caption)
        run = par.add_run()
        run.add_ptab(Alignment.RIGHT,Leader(leader_type),PTab_RelativeTo.MARGIN)
        run.add_field(f"PAGEREF {identifier} \\* MERGEFORMAT",init_value="1")
        run.add_break()

    return RawBlock(par.to_string(),format="openxml")

def add_docx_list(target_block,items,title,heading_style_name="TOCHeading",body_style_name="TOC1",leader_type="middleDot",east_asian_lang=None):
    parent = target_block.parent
    target_idx = parent.content.index(target_block)

    del parent.content[target_idx]

    body = docx_list_body(items,leader_type,body_style_name,east_asian_lang)
    parent.content.insert(target_idx,body)
    
    heading = docx_list_heading(title,heading_style_name,east_asian_lang)
    parent.content.insert(target_idx,heading)

