"""
Module for creating a list of items in a Word document.

Similar functionality can be achieved by adding files such as `html_list.py` to this filter.
"""
from .oxml import *
from panflute import RawBlock

def docx_list_header(title,style_name="TOCHeading",east_asian_lang=None):
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

def docx_list_body(items,leader_length_str="14.64 cm",leader_type="dot",style_name="TOC1",east_asian_lang=None):
    # Create a paragraph with the specified style and tabs
    par = Paragraph()
    par_prop = ParagraphProperty()
    tabs = [
        TabStop(position=0,alignment="left"),
        TabStop(position=parse_strlength(leader_length_str),alignment="right",leader=leader_type)
    ]
    par_prop.set_tabs(tabs)
    par_prop.set_style(style_name)
    if east_asian_lang:
        par_prop.set_eastAsian(east_asian_lang)
    par.set_property(par_prop)

    # Add the items to the paragraph
    for caption,identifier in items:
        par.add_hyperlink(identifier,caption)
        run = par.add_run()
        run.add_tab()
        run.add_field("PAGEREF identifier \\* MERGEFORMAT",init_value="1")
        run.add_break()

    return RawBlock(par.to_string(),format="openxml")