from .lang_num import language_functions
import logging
logger = logging.getLogger('pandoc-tex-numbering')

def header_fields(header_nums):
    fields = {
        f"h{i+1}": header_nums[i] for i in range(len(header_nums))
    }
    for lang,func in language_functions.items():
        fields.update({
            f"h{i+1}_{lang}": func(header_nums[i]) for i in range(len(header_nums))
        })
    return fields

def nums2fields(nums,item_type,num_style="plain",prefix=None,pref_space=True,parent=None):
    parent_num = parent.ref if not parent is None else ""
    if num_style == "plain":
        this_num = str(nums[-1])
    else:
        assert num_style in language_functions, f"Invalid num_style: {num_style}, must be one of {list(language_functions.keys())}"
        this_num = language_functions[num_style](nums[-1])
    num = f"{parent_num}.{this_num}" if parent_num!="" else this_num
    common_fields = {
        "num": num,
        "parent_num": parent_num,
        "this_num": this_num,
    }
    if not prefix is None:
        prefix = prefix.strip()
        prefix = prefix + " " if pref_space else prefix
        common_fields.update({
            "prefix": prefix.lower(),
            "Prefix": prefix.capitalize()
        })
    if item_type in ["sec","apx"]:
        add_fields = header_fields(nums)
    elif item_type == "subfig":
        add_fields = {
            "fig_id": str(nums[-2]),
            "subfig_id": str(nums[-1]),
            **header_fields(nums[:-2]),
        }
    else:
        add_fields = {
            f"{item_type}_id": str(nums[-1]),
            **header_fields(nums[:-1])
        }
    return {**common_fields,**add_fields}

class Formater:
    def __init__(self,fmt_presets,item_type,num_style="plain",prefix=None,pref_space=True):
        self.fmt_presets = fmt_presets
        self.item_type = item_type
        self.num_style = num_style
        self.prefix = prefix
        self.pref_space = pref_space
    
    def __repr__(self):
        return f"Formater({self.item_type})"
    
    def __call__(self, nums, fmt_preset=None,fmt=None,parent=None):
        if not fmt_preset is None:
            assert fmt_preset in self.fmt_presets, f"Invalid format type: {fmt_preset}"
            fmt = self.fmt_presets[fmt_preset]
        if fmt is None:
            if fmt_preset == "Cref":
                cref = self(nums,fmt_preset="cref",parent=parent)
                return f"{cref[0].upper()}{cref[1:]}"
            elif fmt_preset == "src":
                return self(nums,fmt_preset="Cref",parent=parent)
            else:
                raise ValueError("No valid format provided")
        fields = nums2fields(nums,self.item_type,self.num_style,self.prefix,self.pref_space,parent)
        if isinstance(fmt,str):
            return fmt.format(**fields)
        elif callable(fmt):
            return fmt(nums)

class Numbering:
    def __init__(self,item_type,nums,formater=None,parent=None):
        self.item_type = item_type
        self.nums = nums
        self.formater = formater
        self.caption = None
        self.short_caption = None
        self.parent = parent
    
    def format(self,fmt_preset=None,fmt=None):
        return self.formater(self.nums,fmt_preset,fmt,self.parent)

    @property
    def src(self):
        return self.format(fmt_preset="src")
    
    @property
    def ref(self):
        return self.format(fmt_preset="ref")
    
    @property
    def cref(self):
        return self.format(fmt_preset="cref")
    
    @property
    def Cref(self):
        return self.format(fmt_preset="Cref")
    
    def to_dict(self):
        data = {
            "item_type": self.item_type,
            "nums": self.nums,
            "src": self.src,
            "ref": self.ref,
            "cref": self.cref,
            "Cref": self.Cref,
        }
        if self.caption is not None:
            data["caption"] = self.caption
        if self.short_caption is not None:
            data["short_caption"] = self.short_caption
        return data
    
    def is_next_of(self,value):
        if self.item_type != value.item_type:
            return False
        if len(self.nums) != len(value.nums):
            return False
        return self.nums[:-1] == value.nums[:-1] and self.nums[-1] == value.nums[-1]+1
    
    def __eq__(self, value):
        return self.item_type == value.item_type and self.nums == value.nums
    
    def __gt__(self, value):
        if self.item_type != value.item_type:
            return self.item_type > value.item_type
        else:
            for i in range(min(len(self.nums),len(value.nums))):
                if self.nums[i] != value.nums[i]:
                    return self.nums[i] > value.nums[i]
            return len(self.nums) < len(value.nums)
    
    def __lt__(self, value):
        return (not self.__gt__(value)) and (not self.__eq__(value))
    
    def __repr__(self):
        return f"Numbering({str(self)})"
    
    def __str__(self):
        return f"{self.item_type}: {'.'.join(map(str,self.nums))}"

class NumberingState:
    def __init__(self,formaters:dict,reset_level=1,max_levels=10):
        self.reset_level = reset_level
        self.sec = [0]*max_levels
        self.apx = [0]*max_levels
        self.eq = 0
        self.tab = 0
        self.fig = 0
        self.subfig = 0
        self.thms = {}
        self.formaters = formaters
        self.isin_apx = False

        # We need to store the current numbering objects for each level since they're frequently accessed in the same level. We cannot create a new object each time considering the RAM usage.
        self.current_sec_objs = [None]*max_levels
        self.current_apx_objs = [None]*max_levels

    def next_sec(self,level):
        if self.isin_apx:
            self.apx[level-1] += 1
            self.apx[level:] = [0]*(len(self.apx)-level)
            self.current_apx_objs[level-1:] = [None]*(len(self.current_apx_objs)-level)
        else:
            self.sec[level-1] += 1
            self.sec[level:] = [0]*(len(self.sec)-level)
            self.current_sec_objs[level-1:] = [None]*(len(self.current_sec_objs)-level)
        if level <= self.reset_level:
            self.eq = 0
            self.tab = 0
            self.fig = 0
            self.subfig = 0
    
    def next_eq(self):
        self.eq += 1
    
    def next_tab(self):
        self.tab += 1
    
    def next_fig(self):
        self.fig += 1
        self.subfig = 0
    
    def next_subfig(self):
        self.subfig += 1
    
    def next_thm(self,thm_type):
        if not thm_type in self.thms:
            self.thms[thm_type] = 1
        else:
            self.thms[thm_type] += 1
    
    @property
    def current_sec_nums(self):
        return self.sec[:self.reset_level] if self.isin_apx else self.apx[:self.reset_level]
    
    def current_sec(self,level):
        if level <=0: return None
        if self.isin_apx:
            item_type = "apx"
            obj_list = self.current_apx_objs
            num_list = self.apx
        else:
            item_type = "sec"
            obj_list = self.current_sec_objs
            num_list = self.sec
        if obj_list[level-1] is None:
            obj_list[level-1] = Numbering(item_type,num_list[:level],self.formaters[item_type][level-1],parent=self.current_sec(level-1))
        return obj_list[level-1]
    
    def current_eq(self):
        return Numbering("eq",self.current_sec_nums+[self.eq],self.formaters["eq"],parent=self.current_sec(self.reset_level))
    
    def current_tab(self):
        return Numbering("tab",self.current_sec_nums+[self.tab],self.formaters["tab"],parent=self.current_sec(self.reset_level))
    
    def current_fig(self,subfig=False):
        if subfig:
            return Numbering("subfig",self.current_sec_nums+[self.fig,self.subfig],self.formaters["subfig"],parent=self.current_fig(False))
        else:
            return Numbering("fig",self.current_sec_nums+[self.fig],self.formaters["fig"],parent=self.current_sec(self.reset_level))
    
    def current_thm(self,thm_type):
        if not thm_type in self.thms:
            self.thms[thm_type] = 0
        return Numbering(f"thm-{thm_type}",self.current_sec_nums+[self.thms[thm_type]],self.formaters["thm"][thm_type],parent=self.current_sec(self.reset_level))

def numberings2chunks(numberings,split_continous=True):
    numberings = sorted(numberings)
    chunks = {}
    for num in numberings:
        item_type = num.item_type
        if not item_type in chunks:
            chunks[item_type] = [[num]]
            continue
        last_chunk = chunks[item_type][-1]
        if num.is_next_of(last_chunk[-1]):
            last_chunk.append(num)
        else:
            chunks[item_type].append([num])
    if not split_continous:
        for item_type in chunks:
            chunks[item_type] = [[chunk for chunks in chunks[item_type] for chunk in chunks]]
    return chunks

if __name__ == "__main__":
    print(Numbering("sec",[3]).is_next_of(Numbering("sec",[2,1])))
    numberings = [
        Numbering("sec",[2,1],None),
        Numbering("sec",[3],None),

        # Numbering("eq",[1,5],None),
        # Numbering("eq",[1,2],None),
        # Numbering("eq",[1,3],None),

        # Numbering("tab",[1,2],None),
        # Numbering("tab",[1,3],None),
        # Numbering("tab",[1,1],None),
    ]
    chunks = numberings2chunks(numberings,False)
    print(chunks)
    # sec_num_fmts = ["{num}"]*10
    # sec_ref_fmts = [prefix2ref_fmt("Section")]*10
    # state = NumberingState(sec_num_fmts=sec_num_fmts,sec_ref_fmts=sec_ref_fmts,subfig_syms=["a","b","c","d","e","f","g","h","i","j"])
    # state.next_sec(1)
    # state.next_sec(2)
    # state.next_sec(3)
    # state.next_eq()
    # state.next_tab()
    # state.next_fig()
    # state.next_subfig()
    # state.next_subfig()
    # state.next_subfig()
    # print(state.current_sec(1).num)
    # print(state.current_sec(2).num)
    # print(state.current_sec(3).ref)
    # print(state.current_eq().ref)
    # print(state.current_tab().Ref)
    # print(state.current_fig().Ref)
    # print(state.current_fig(subfig=True).num)
    # print(state.current_fig(subfig=True).ref)
    # print(state.current_fig(subfig=True).Ref)
    # print(state.current_fig(subfig=True).to_dict())
