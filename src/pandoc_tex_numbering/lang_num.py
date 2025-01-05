# Here, we define the functions to convert arabic numbers to different languages
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

language_functions = {
    "zh": arabic2chinese
}