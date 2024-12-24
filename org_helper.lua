function RawBlcok (elem)
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
