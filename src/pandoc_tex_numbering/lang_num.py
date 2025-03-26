# Here, we define the functions to convert arabic numbers to different languages
def _num2base(num,base):
    if num == 0: return [0]
    nums = []
    while num > 0:
        num, r = divmod(num, base)
        nums.append(r)
    return nums[::-1]

def _from_seq(seq,num,zero_str="0"):
    if num == 0:
        return zero_str
    nums = _num2base(num-1,len(seq))
    return "".join([seq[n] for n in nums])

def arabic2chinese(num):
    chinese_numerals = "零一二三四五六七八九"
    units = ["", "十", "百", "千", "万", "十", "百", "千", "亿"]
    result = ""
    num_str = str(num)
    length = len(num_str)
    
    for i in range(length):
        digit = int(num_str[i])
        if digit != 0:
            result += chinese_numerals[digit] + units[length - i - 1]
        else:
            if not result.endswith("零"):
                result += "零"
    if result!="零":
        result = result.rstrip("零")
    if result.startswith("一十"):
        result = result[1:]
    return result

def arabic2upper_roman(num):
    if num == 0: return "0"
    breaks = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
    numerals = ["M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"]
    result = ""
    while num>0:
        for b,n in zip(breaks,numerals):
            if num >= b:
                result += n
                num -= b
                continue
    return result

def arabic2lower_roman(num):
    return arabic2upper_roman(num).lower()

def arabic2upper_latin(num):
    upper_latin_numerals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return _from_seq(upper_latin_numerals,num)

def arabic2lower_latin(num):
    lower_latin_numerals = "abcdefghijklmnopqrstuvwxyz"
    return _from_seq(lower_latin_numerals,num)

def arabic2upper_greek(num):
    upper_greek_numerals = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    return _from_seq(upper_greek_numerals,num)

def arabic2lower_greek(num):
    lower_greek_numerals = "αβγδεζηθικλμνξοπρστυφχψω"
    return _from_seq(lower_greek_numerals,num)

def arabic2lower_cyrillic(num):
    lower_cyrillic_numerals = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    return _from_seq(lower_cyrillic_numerals,num)

def arabic2upper_cyrillic(num):
    upper_cyrillic_numerals = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    return _from_seq(upper_cyrillic_numerals,num)

language_functions = {
    "zh": arabic2chinese,
    "Roman": arabic2upper_roman,
    "roman": arabic2lower_roman,
    "latin": arabic2lower_latin,
    "Latin": arabic2upper_latin,
    "grekk": arabic2lower_greek,
    "Greek": arabic2upper_greek,
    "cyrillic": arabic2lower_cyrillic,
    "Cyrillic": arabic2upper_cyrillic
}