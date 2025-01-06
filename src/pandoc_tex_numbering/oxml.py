"""
This module provides a set of classes to generate OpenXML elements in a more friendly way. Referenced from python-docx library. The API provided here is far more lightweight and avoids the dependency on python-docx.

Based on this, we can directly add custom items to docx in the filter utilizing the RawBlock(format:openxml) in pandoc.
"""
import xml.etree.ElementTree as ET
from enum import Enum

class ElementProxy:
    # Here we wrap the ElementTree.Element class to provide a lazy evaluation of the element and a more flexible and friendly interface
    def __init__(self,elem_name,children=None,attrs=None,text=None):
        self.elem_name = elem_name
        self.attrs = attrs or {}
        self.children = children or []
        self.text = text
    
    def append(self,child):
        self.children.append(child)
    
    def set_attrs(self,attr_dict):
        self.attrs.update(attr_dict)
    
    def search_children(self,elem_name):
        return [child for child in self.children if child.elem_name == elem_name]
    
    def get_or_create_child(self,elem_name):
        children = self.search_children(elem_name)
        if children:
            return children[0]
        child = ElementProxy(elem_name)
        self.append(child)
        return child
    
    def remove_child(self,elem_name):
        self.children = [child for child in self.children if child.elem_name != elem_name]
    
    @property
    def element(self):
        elm = ET.Element(self.elem_name)
        for k,v in self.attrs.items():
            elm.set(k,v)
        for child in self.children:
            child_elem = child.element if isinstance(child,ElementProxy) else child
            elm.append(child_elem)
        if self.text:
            elm.text = self.text
        return elm
    
    def to_string(self,encoding="utf-8"):
        return ET.tostring(self.element,xml_declaration=False,encoding=encoding).decode()

# define some enums
class Alignment(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"

class Leader(Enum):
    DOT = "dot"
    HYPHEN = "hyphen"
    UNDERSCORE = "underscore"
    NONE = "none"
    MIDDLE_DOT = "middleDot"

class PTab_RelativeTo(Enum):
    MARGIN = "margin"
    INDENT = "indent"

class Run(ElementProxy):
    def __init__(self,children=None,attrs=None):
        super().__init__("w:r",children,attrs)

    def add_field(self,field_code,init_value=""):
        field_elems = [
            ElementProxy("w:fldChar",attrs={"w:fldCharType":"begin"}),
            ElementProxy("w:instrText",attrs={"xml:space":"preserve"}),
            ElementProxy("w:instrText",text=field_code),
            ElementProxy("w:fldChar",attrs={"xml:space":"preserve"}),
            ElementProxy("w:fldChar",attrs={"w:fldCharType":"separate"}),
            ElementProxy("w:t",text=init_value),
            ElementProxy("w:fldChar",attrs={"w:fldCharType":"end"})
        ]
        for elem in field_elems:
            self.append(elem)
    
    def add_tab(self):
        tab = TabStop()
        self.append(tab)
        return tab
    
    def add_break(self):
        break_elem = ElementProxy("w:br")
        self.append(break_elem)
        return break_elem
    
    def add_text(self,text):
        text_elem = ElementProxy("w:t",text=text)
        self.append(text_elem)
        return text_elem
    
    def add_ptab(self,alignment:Alignment,leader:Leader,relative_to:PTab_RelativeTo):
        ptab = PTabStop(alignment,leader,relative_to)
        self.append(ptab)
        return ptab

class PTabStop(ElementProxy):
    def __init__(self,alignment:Alignment=Alignment.LEFT,leader:Leader=Leader.NONE,relative_to:PTab_RelativeTo=PTab_RelativeTo.MARGIN):
        super().__init__("w:ptab",attrs={
            "w:alignment":alignment.value,
            "w:leader":leader.value,
            "w:relativeTo":relative_to.value
        })

class HyperLink(ElementProxy):
    def __init__(self,identifier,text,style=None):
        super().__init__("w:hyperlink",children=[
            Run(children=[ElementProxy("w:t",text=text)])
        ],attrs={"w:anchor":identifier,"w:history":"1"})

class Paragraph(ElementProxy):
    def __init__(self,children=None,attrs=None):
        super().__init__("w:p",children,attrs)
    
    def add_hyperlink(self,identifier,text,style=None):
        hyperlink = HyperLink(identifier,text,style)
        self.append(hyperlink)
        return hyperlink
    
    def add_run(self,children=None,attrs=None):
        run = Run(children,attrs)
        self.append(run)
        return run
    
    def set_property(self,prop:'ParagraphProperty'):
        self.remove_child("w:pPr")
        self.append(prop)


class TabStop(ElementProxy):
    def __init__(self,position=None,alignment:Alignment=Alignment.LEFT,leader:Leader=Leader.NONE):
        super().__init__("w:tab",attrs={
            "w:val":alignment.value,
            "w:leader":leader.value
        })
        if position:
            self.set_attrs({"w:pos":str(position)})

class ParagraphProperty(ElementProxy):
    def __init__(self,children=None,attrs=None):
        super().__init__("w:pPr",children,attrs)
    
    def set_style(self,style_name):
        style = self.get_or_create_child("w:pStyle")
        style.set_attrs({"w:val":style_name})
    
    def set_tabs(self,tabs:list[TabStop]):
        self.remove_child("w:tabs")
        tabs_elem = ElementProxy("w:tabs")
        for tab in tabs:
            tabs_elem.append(tab)
        self.append(tabs_elem)
    
    def set_eastAsian(self,lang="zh-CN"):
        lang_elem = self.get_or_create_child("w:lang")
        lang_elem.set_attrs({"w:eastAsia":lang})
        self.append(lang_elem)

length2twip = {
    "in":lambda x: int(x*1440),
    "cm":lambda x: int(x*567), # 2.54 cm ≈ 1 inch, 72/2.54*20 ≈ 567
    "mm":lambda x: int(x*56.7),
    "pt":lambda x: int(x*20),
    "emu":lambda x: int(x/635),
    "twip":lambda x: int(x)
}

twip2length = {
    "in":lambda x: x/1440,
    "cm":lambda x: x/567,
    "mm":lambda x: x/56.7,
    "pt":lambda x: x/20,
    "emu":lambda x: x*635,
    "twip":lambda x: x
}

class Length:
    def __init__(self,value,unit="cm"):
        self.value = value
        self.unit = unit
        self.twip = length2twip[unit](value)
    
    def to_unit(self,unit):
        return twip2length[unit](self.twip)
    
    def __str__(self):
        return f"{self.value} {self.unit}"
    
    def __repr__(self):
        return f"Length({self.value},{self.unit})={self.twip} twip"
    
    @staticmethod
    def from_string(value):
        items = value.strip().split(" ")
        if len(items) == 2:
            value,unit = items
            try:
                value = float(value)
                return Length(value,unit)
            except:
                raise ValueError("Invalid length value")
        raise ValueError("Invalid length string")
