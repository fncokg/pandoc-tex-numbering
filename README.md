# pandoc-tex-numbering
This is an all-in-one pandoc filter especially for LaTeX files to keep **numbering, hyperlinks, caption prefixs and cross references in (maybe multi-line) equations, sections, figures, and tables**.

With `pandoc-tex-numbering`, you can convert your LaTeX source codes to any format pandoc supported, especially `.docx`, while **keep all your auto-numberings and cross references**.

`pandoc-tex-numbering` also supports:
- **Multi-line environments** in LaTeX math block such as `align`, `cases` etc.
- **Non-arabic numbers** for the section numbering such as Chinese numbers "第一章", "第二节" etc.
- **`cleveref` package** and even more clever cross-references customization.

# Installation

1. Install `pandoc` and `python3` if you haven't.
2. Install python package `panflute` and `pylatexenc` if you haven't:
```bash
pip install panflute pylatexenc
```
3. Download the `pandoc-tex-numbering.py` and put it in your PATH or in the same directory as your LaTeX source file.

# Usage

## Quick Start

Take `.docx` as an example:

```bash
pandoc --filter pandoc-tex-numbering.py input.tex -o output.docx
```

Note 1: (*skip this if you are working on `.tex` files*) The filter is designed for LaTeX files but, technically, it can also work with any LaTeX-like documents as long as `pandoc` is able to parse them in a LaTeX-like AST. For example, it can work with `.org` files with the help of an additional lua filter `org_helper.lua`. See the [org file support](#org-file-support) section for more details.

Note 2: By default, the filter will number the sections, figures, tables, and equations. In case you only want to number some of them (for example in case you want to number only equations with this filter while number others with other filters), you can set the corresponding variables in the metadata of your LaTeX file. See the [Customization](#customization) section for more details.

## Customization

You can set the following variables in the metadata of your LaTeX file to customize the behavior of the filter:

### General
- `number-figures`: Whether to number the figures. Default is `True`.
- `number-tables`: Whether to number the tables. Default is `True`.
- `number-equations`: Whether to number the equations. Default is `True`.
- `number-sections`: Whether to number the sections. Default is `True`.
- `number-reset-level`: The level of the section that will reset the numbering. Default is 1. For example, if the value is 2, the numbering will be reset at every second-level section and shown as "1.1.1", "3.2.1" etc.

### Equations
- `multiline-environments`: Possible multiline environment names separated by commas. Default is "cases,align,aligned,gather,multline,flalign". The equations under these environments will be numbered line by line.

### `cleveref` Support
Currently, pandoc's default LaTeX reader does not support `\crefname` and `Crefname` commands (they are not visible in the AST for filters). To support cleveref package, you can set the following metadata:
- `figure-prefix`: The prefix of the figure reference. Default is "Figure".
- `table-prefix`: The prefix of the table reference. Default is "Table".
- `equation-prefix`: The prefix of the equation reference. Default is "Equation".
- `section-prefix`: The prefix of the section reference. Default is "Section".
- `prefix-space`: Whether to add a space between the prefix and the number. Default is `True` (for some languages, the space may not be needed).

**Note: multiple references are not supported currently.** Try to use `Figures \ref{fig:1} and \ref{fig:2}` instead of `\cref{fig:1,fig:2}` for now.

### Custom Section Numbering Format
For the section numbering, you can customize the format of the section numbering added at the beginning of the section titles and used in the references. The following metadata are used. For more details, see the [Details of Sections](#sections) section.
- `section-format-source-1`, `section-format-source-2`,...: The format of the section numbering at each level. Default is `"{h1}"`, `"{h1}.{h2}"` etc.
- `section-format-ref-1`, `section-format-ref-2`,...: The format of the section numbering used in the references. **If set, this will override the `section-prefix` metadata**. Default is `"{h1}"`, `"{h1}.{h2}"`, etc. combined with the `section-prefix` and `prefix-space` metadata.
- `non-arabic_numbers`: Whether to use non-arabic numbers for the section numbering. Default is `False`. If set to `True`, all non arabic section fields are also supported, and in this case, **the `lang_num.py` file must also be included in the same directory as the filter.**

### Caption Renaming
The `figure-prefix` and `table-prefix` metadata are also used to rename the captions of figures and tables.

## `org` file support

`org` files are supported by adding an additional lua filter `org_helper.lua` to the pandoc command. The usage is as follows:

```bash
pandoc --lua-filter org_helper.lua --filter pandoc-tex-numbering.py input.org -o output.docx
```

**Be sure to use `--lua-filter org_helper.lua` before `--filter pandoc-tex-numbering.py`**.

Reason for this is the default `org` reader of `pandoc` does not parse LaTeX codes by default, for example, LaTeX equations in `equation` environments and cross references via `\ref{}` macros are parsed as `RawBlock` and `RawInline` nodes, while we desire `Math` nodes and `Link` nodes respectively. The `org_helper.lua` filter helps read these blocks via `latex` reader and after that, the `pandoc-tex-numbering.py` filter can work as expected.

Related discussions can also be found in [pandoc issue #1764](https://github.com/jgm/pandoc/issues/1764) (codes in `org_helper.lua` are based on comments from @tarleb in this issue) and [pandoc-tex-numbering issue #1](https://github.com/fncokg/pandoc-tex-numbering/issues/1).

# Details

## Equations

If metadata `number-equations` is set to `True`, all the equations will be numbered. The numbers are added at the end of the equations and the references to the equations are replaced by their numbers.

Equations under multiline environments (specified by metadata `multiline-environments` ) such as `align`, `cases` etc. are numbered line by line, and the others are numbered as a whole block.

That is to say, if you want the filter to number multiline equations line by line, use `align`, `cases` etc. environments directly. If you want the filter to number the whole block as a whole, use `split`, `aligned` etc. environments in the `equation` environment.

For example, as shown in `test_data/test.tex`:

```latex
\begin{equation}
    \begin{aligned}
        f(x) &= x^2 + 2x + 1 \\
        g(x) &= \sin(x)
    \end{aligned}
    \label{eq:quadratic}
\end{equation}
```

This equation will be numbered as a whole block, say, (1.1), while:

```latex
\begin{align}
    a &= b + c \label{eq:align1} \\
    d &= e - f \label{eq:align2}
\end{align}
```

This equation will be numbered line by line, say, (1.2) and (1.3)

**NOTE: the pandoc filters have no access to the difference of `align` and `align*` environments.** Therefore, you CANNOT turn off the numbering of a specific `align` environment via the `*` mark. *This may be fixed by a custom lua reader to keep those information in the future.*

## Sections

If metadata `number-sections` is set to `True`, all the sections will be numbered. The numbers are added at the beginning of the section titles and the references to the sections are replaced by their numbers.

You can customize the format of the section numbering added at the beginning of the section titles and used in the references by setting the metadata `section-format-source-1`, `section-format-source-2`, etc. and `section-format-ref-1`, `section-format-ref-2`, etc. All of these metadata accept a python f-string format with fields `h1`, `h2`, ..., `h10` representing the numbers of each level headers. 

For example, to add a prefix "Chapter" and a suffix "." to the first-level section, you can set `section-format-source-1` to `"Chapter {h1}."`. At the beginning of the first-level section, it will be shown as "Chapter 1.". And if you also want to add the prefix "Chapter" to the references, but without the suffix ".", you can set `section-format-ref-1` to `"Chapter {h1}"`. Then, when a first-level section is referred to, it will be shown as "Chapter 1".

The default values of `section-format-source-1`, `section-format-source-2`, etc. are in fact `{h1}`, `{h1}.{h2}`, etc. respectively, and the default values of `section-format-ref-1`, `section-format-ref-2`, etc. are in fact `{h1}`, `{h1}.{h2}` combined with the `section-prefix` and `prefix-space` metadata respectively.

Sometimes, non arabic numberings are needed. For example, in Chinese, with `section-format-source-1="第{h1}章"`, the users get "第1章", "第2章" etc. However, sometimes the users may need "第一章", "第二章" etc. To achieve this, we also support non arabic numbers by series of non-arabic fields. For example, when `{h1}` is 12, the Chinese number field `{h1_zh}` will be "十二". To enable this feature, you need to:

- set `non-arabic-numbers` to `True` in the metadata.
- include the `lang_num.py` file in the same directory as the filter.
- set `section-format-source-1="第{h1_zh}章"` and `section-format-ref-1="第{h1_zh}章"` in the metadata.

Note that:
- The non-arbic number support is by default turned off. You need to explicitly turn it on.
- The current version only supports simplified Chinese numbers. If you need other languages, you can modify the `lang_num.py` file. See the [Custom Non-Arabic Numbers Support](#custom-non-arabic-numbers-support) section for more details.

## Figures and Tables

All the figures and tables are supported. All references to figures and tables are replaced by their numbers, and all the captions are added prefixs such as "Figure 1.1: ".

You can determine the prefix of figures and tables by changing the variables `figure-prefix` and `table-prefix` in the metadata, default values are "Figure" and "Table" respectively.

## Log

Some warning message will be shown in the log file named `pandoc-tex-numbering.log` in the same directory as the output file. You can check this file if you encounter any problems or report those messages in the issues.

# Examples

With the testing file `testing_data/test.tex`:

## Default Metadata

```bash
pandoc -o output.docx -F pandoc-tex-numbering.py test.tex 
```

The results are shown as follows:

![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/default-page1.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/default-page2.jpg?raw=true)

## Customized Metadata

In the following example, we custom the following (maybe silly) items *only for the purpose of demonstration*:
- Use all prefixes as "Fig", "Tab", "Eq" respectively.
- Reset the numbering at the second level sections, such that the numbering will be shown as "1.1.1", "3.2.1" etc.
- At the beginning of sections, use Chinese numbers "第一章" for the first level sections and English numbers "Section 1.1" for the second level sections.
- When referred to, use, in turn, "Chapter 1", "第1.1节" etc.

**In this case, please note that the `lang_num.py` file must be also included in the same directory as the filter.**

Run the following command with corresponding metadata in a `metadata.yaml` file (**recommended**):

```bash
pandoc -o output.docx -F pandoc-tex-numbering.py --metadata-file test.yaml test.tex
```

```yaml
# test.yaml
figure-prefix: Fig
table-prefix: Tab
equation-prefix: Eq
number-reset-level: 2
non-arabic-numbers: true
section-format-source-1: "第{h1_zh}章"
section-format-source-2: "Section {h1}.{h2}."
section-format-ref-1: "Chapter {h1}"
section-format-ref-2: "第{h1}.{h2}节"
```

The results are shown as follows:
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page1.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page2.jpg?raw=true)

# Development

## Custom Non-Arabic Numbers Support

Currently, the filter supports only Chinese non-arabic numbers. If you want to support other languages, you can modify the `lang_num.py` file. For example, if you want to support the non-arabic numbers in the language `foo`, you can:

1. Define a new function `arabic2foo(num:int)->str` that converts the arabic number to the corresponding non-arabic number.
2. Add the function to the `language_functions` dictionary with the corresponding language name as the key, for example `{"foo":arabic2foo}`.

Then you can set the metadata `section-format-1="Chapter {h1_foo}."` to enable the non-arabic numbers in the filter.

## Custom Numbering Format

To keep the design of the filter simple and easy to use, the filter only supports a limited number of numbering formats. However, complex formats can easily be extended by modifying the logic in the `action_replace_refs` function.

## Extend the Filter

The logical structure of the filter is quiet straightforward. You can see this filter as a scaffold for your own filter. For example, `_parse_multiline_environment` function receives a latex math node and the doc object and returns a new modified math string with the numbering and respective labels. You can add your customized latex syntax analysis logic to support more complicated circumstances.

It is recommended to decalre all your possible variables in the `prepare` function, and save them in the `doc.pandoc_tex_numbering:dict` object. This object will be automatically destroyed after the filter is executed.

# TODO

There are some known issues and possible improvements:
- [ ] Support multiple references in `cleveref` package.
- [ ] Add empty cpation for figures and tables without captions (currently, they have no caption and therefore links to them cannot be located).
- [ ] Support `align*` and other non-numbered environments.