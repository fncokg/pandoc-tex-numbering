"""
This module provides a set of classes to generate OpenXML elements in a more friendly way. Referenced from python-docx library. The API provided here is far more lightweight and avoids the dependency on python-docx.

Based on this, we can directly add custom items to docx in the filter utilizing the RawBlock(format:openxml) in pandoc.
"""
import xml.etree.ElementTree as ET

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
    def __init__(self,position=None,alignment=None,leader=None):
        super().__init__("w:tab",attrs={})
        if position:
            self.set_attrs({"w:pos":str(position)})
        if alignment:
            self.set_attrs({"w:val":alignment})
        if leader:
            self.set_attrs({"w:leader":leader})

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

_length = {
    "in":lambda x: int(x*1440),
    "cm":lambda x: int(x*567), # 2.54 cm ≈ 1 inch, 72/2.54*20 ≈ 567
    "mm":lambda x: int(x*56.7),
    "pt":lambda x: int(x*20),
    "emu":lambda x: int(x/635),
    "twip":lambda x: int(x)
}

def length2twip(value,unit="cm"):
    return _length[unit](value)

def parse_strlength(value):
    items = value.strip().split(" ")
    if len(items) == 2:
        value,unit = items
        try:
            value = float(value)
            return length2twip(value,unit)
        except:
            raise ValueError("Invalid length value")
    raise ValueError("Invalid length string")
