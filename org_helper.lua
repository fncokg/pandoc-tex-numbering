function RawBlock (elem)
  if elem.format == "latex" then
    local res = pandoc.read(elem.text, "latex")
    return pandoc.Div(res.blocks)
  else
    return elem
  end
end

function RawInline (elem)
  if elem.format == "latex" then
    local res = pandoc.read(elem.text, "latex")
    return res.blocks[1].content[1]
  else
    return elem
  end
end

function Str (elem)
  local text,count = string.gsub(elem.text, "eqref:(.*)", "\\ref{%1}")
  if count > 0 then
    return pandoc.read(text, "latex").blocks[1].content[1]
  else
    return elem
  end
end
