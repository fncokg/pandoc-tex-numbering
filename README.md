# pandoc-tex-numbering
This is an all-in-one pandoc filter for converting your LaTeX files to any format while keeping **numbering, hyperlinks, caption formats and (clever) cross references in (maybe multi-line) equations, sections, figures, and tables**. The formating is highly customizable, easy-to-use, and even more flexible than the LaTeX default.

# Contents
- [pandoc-tex-numbering](#pandoc-tex-numbering)
- [Contents](#contents)
- [What do we support?](#what-do-we-support)
- [Installation](#installation)
  - [From PyPI (Recommended)](#from-pypi-recommended)
  - [From Source](#from-source)
- [Quick Start](#quick-start)
- [Customization](#customization)
  - [General](#general)
  - [Formatting System](#formatting-system)
    - [Prefix-based System](#prefix-based-system)
    - [Custom Formatting System (f-string formatting)](#custom-formatting-system-f-string-formatting)
      - [Metadata Names](#metadata-names)
      - [Metadata Values](#metadata-values)
  - [Equations](#equations)
  - [List of Figures and Tables](#list-of-figures-and-tables)
  - [Multiple References](#multiple-references)
- [Details](#details)
  - [Equations](#equations-1)
  - [List of Figures and Tables](#list-of-figures-and-tables-1)
  - [Data Export](#data-export)
  - [Log](#log)
  - [`org` file support](#org-file-support)
- [Examples](#examples)
  - [Default Metadata](#default-metadata)
  - [Customized Metadata](#customized-metadata)
- [Development](#development)
  - [Custom Non-Arabic Numbers Support](#custom-non-arabic-numbers-support)
  - [Custom Numbering Format](#custom-numbering-format)
  - [Extend the Filter](#extend-the-filter)
  - [Advanced docx Support](#advanced-docx-support)
- [FAQ](#faq)
- [TODO](#todo)

# What do we support?
- **Multi-line Equations**: Multi-line equations in LaTeX math block such as `align`, `cases` can be numbered line by line. `\nonumber` commands are supported to turn off the numbering of a specific line.
- **`cleveref` Package**: `cref` and `Cref` commands are supported. You can customize the prefix of the references.
- **Subfigures**: `subcaption` package is supported. Subfigures can be numbered with customized symbols and formats.
- **Non-Arabic Numbers**: Chinese numbers "第一章", "第二节" etc. are supported. You can customize the numbering format.
- **Custom List of Figures and Tables**: **Short captions** as well as custom lof/lot titles are supported for figures and tables.
- **Custom Formatting of Everything**: You can customize the format of the numbering and references with python f-string format based on various fields we provide.

# Installation

First, install `pandoc` and `python3` if you haven't. Then you can install the filter via one of the following methods:

## From PyPI (Recommended)

In Python>=3.8 `pandoc-tex-numbering` can be installed via `pip`:

```bash
pip install pandoc-tex-numbering
```

## From Source

**Only in case you want to use the filter with a lower version of Python (under 3.8)**, you can download the source code (i.e. all files under `src/pandoc_tex_numbering`) manually and put it in the same directory as your source file. In this case, when using the filter, you should specify the filter file via `-F pandoc-tex-numbering.py` instead of `-F pandoc-tex-numbering`.

# Quick Start

Take `.docx` as an example:

```bash
pandoc -F pandoc-tex-numbering -o output.docx input.tex 
```

# Customization

You can set the following variables in the metadata of your LaTeX file to customize the behavior of the filter:

## General
- `number-figures`: Whether to number the figures. Default is `true`.
- `number-tables`: Whether to number the tables. Default is `true`.
- `number-equations`: Whether to number the equations. Default is `true`.
- `number-sections`: Whether to number the sections. Default is `true`.
- `number-reset-level`: The level of the section that will reset the numbering. Default is 1. For example, if the value is 2, the numbering will be reset at every second-level section and shown as "1.1.1", "3.2.1" etc.
- `section-max-levels`: The maximum level of the section numbering. Default is 10.
- `data-export-path`: Where to export the filter data. Default is `None`, which means no data will be exported. If set, the data will be exported to the specified path in the JSON format. This is useful for further usage of the filter data in other scripts or filter-debugging.
- `auto-labelling`: Whether to automatically add identifiers (labels) to figures and tables without labels. Default is `true`. This has no effect on the output appearance but can be useful for cross-referencing in the future (for example, in the `.docx` output this will ensure that all your figures and tables have a unique auto-generated bookmark).

## Formatting System

We support a very flexible formatting system for the numbering and references. There are two different formatting systems for the numbering and references. You can use them together. The two systems are:

- Prefix-based System: This is lightweight and easy to use. When referenced, a corresponding prefix will automatically added to the number.
- Custom Formatting System: This is more flexible and powerful. You can customize the format of the numbering and references with python f-string format based on various fields we provide.

### Prefix-based System
The following metadata are used for the prefix-based system:
- `figure-prefix`: The prefix of the figure reference. Default is "Figure".
- `table-prefix`: The prefix of the table reference. Default is "Table".
- `equation-prefix`: The prefix of the equation reference. Default is "Equation".
- `section-prefix`: The prefix of the section reference. Default is "Section".
- `prefix-space`: Whether to add a space between the prefix and the number. Default is `true` (for some languages, the space may not be needed).

### Custom Formatting System (f-string formatting)

#### Metadata Names
For now, we support 5 types of items and 4 types of formatting:
- Item types: `fig` (figure), `tab` (table), `eq` (equation), `sec` (section), `subfig` (subfigure).
- Formatting types: 
  - `src` (source): The format of the numbering where the item appears. For figures and tables, this is the format used in the captions. For equations, this is the format used after the equations. For sections, this is the format used at the beginning of the section titles.
  - `ref` (reference): The format of numbering used in `\ref` command.
  - `cref` (cleveref reference)/`Cref` (Cleveref reference with capital letter): The format of numbering used in `\cref` and `\Cref` commands.

You can customize the formatting type `b` of the item type `a` by setting the metadata `a-b-format`. For example, to customize the numbering format of figure captions, you set the `fig-src-format` metadata.

By default, **if not specified**, the `Cref` format will be the capitalized version of the `cref` format, the `src` format will be the same as the `Cref` format, the `ref` format will be `"{num}"`, and the `cref` format will be `"{prefix}{num}"`.

For sections, every level has its own formatting. You can set the metadata, for example, `section-src-format-1`, `section-cref-format-2`, etc.

For equations, the default `src` format (i.e. `equation-src-format`) is `"\\qquad({num})"`. `\qquad` is used to offer a little space between the equation and the number. You can customize it as you like.

#### Metadata Values
The metadata values are python f-string format strings. Various fields are provided for you to customize the format. For example, if you set the `number-reset-level` to 2, `figure-prefix` to `figure` and `prefix-space` to `True`. Then, the fifth figure under subsection 2.3 will have the following fields:
- `num`: `2.3.5`
- `parent_num`: `2.3`
- `fig_id`: `5`
- `prefix`: `figure ` (note the space at the end)
- `Prefix`: `Figure `
- `h1`: `2`
- `h2`: `3`
- `h1_zh`: `二` (Chinese number support)
- `h2_zh`: `三`

For the subfigures, a special field `subfig_sym` is provided to represent the symbol of the subfigure. For example, if you set the `subfigure-symbols` metadata to `"αβγδ"`, the second subfigure will have the `subfig_sym` field as `"β"` while the `subfig_id` field as `2`.

Here are some examples of the metadata values:
- set the `fig-src-format` metadata to `"{prefix}{num}"`, the numbering before its caption will be shown as "Figure 2.3.5"
- set the `fig-cref-format` metadata to `"{Prefix} {fig_id} (in Section {parent_num})"`, when referred to by `\Cref`, it will be shown as `"Figure 5 (in Section 2.3)"`.
- set the `section-src-format-1` metadata to `"第{h1_zh}章"` and `section-cref-format-1` to `"第{h1_zh}章"` to use Chinese numbers for the first level sections.

For more non-arabic number support, see the [Custom Non-Arabic Numbers Support](#custom-non-arabic-numbers-support) section.

For more examples, see also the [Customized Metadata Examples](#customized-metadata).

## Equations
- `multiline-environments`: Possible multiline environment names separated by commas. Default is "cases,align,aligned,gather,multline,flalign". The equations under these environments will be numbered line by line.

## List of Figures and Tables
To support short captions and custom titles in the list of figures and tables, you can set the following metadata to turn on the custom list of figures and tables:
- `custom-lof`: Whether to use a custom list of figures. Default is `false`.
- `custom-lot`: Whether to use a custom list of tables. Default is `false`.

You can customize the list of figures and tables by setting the following metadata:
- `lof-title`: The title of the list of figures. Default is "List of Figures".
- `lot-title`: The title of the list of tables. Default is "List of Tables".
- `list-leader-type`: The type of leader used in the list of figures and tables (placeholders between the caption and the page number). Default is "dots". Possible values are "dot", "hyphen", "underscore", "middleDot" and "none".

For more details, see the [List of Figures and Tables](#list-of-figures-and-tables) section.

## Multiple References
- `multiple-ref-suppress`: Whether to suppress the multiple references. Default is `true`. If set to `true`, the multiple references will be suppressed. For example, if you have `\cref{eq1,eq2,eq3,eq4}`, it will be shown as "equations 1-4" instead of "equations 1, 2, 3 and 4".
- `multiple-ref-separator`: The separator between the multiple references. Default is ", ". For example, if you set it to "; ", the multiple references will be shown as "equations 1; 2; 3 and 4".
- `multiple-ref-last-separator`: The separator between the last two references. Default is " and ". For example, if you set it to " & ", the multiple references will be shown as "equations 1, 2, 3 & 4".
- `multiple-ref-to`: The separator between suppressed multiple references. Default is "-". For example, if you set it to " to ", the multiple references will be shown as "equations 1 to 4".

NOTE: in case of setting metadata in a yaml file, the spaces at the beginning and the end of the values are by default stripped. Therefore, if you want to keep the spaces in the yaml metadata file, **you should mannually escape those spaces via double slashes.** For example, if you want set `multiple-ref-last-separator` to `" and "` (spaces appear at the beginning and the end), you should set it as `"\\ and\\ "` in the yaml file. See pandoc's [issue #10539](https://github.com/jgm/pandoc/issues/10539) for more further discussions.

# Details

## Equations

If metadata `number-equations` is set to `true`, all the equations will be numbered. The numbers are added at the end of the equations and the references to the equations are replaced by their numbers.

Equations under multiline environments (specified by metadata `multiline-environments` ) such as `align`, `cases` etc. are numbered line by line, and the others are numbered as a whole block.

That is to say, if you want the filter to number multiline equations line by line, use `align`, `cases` etc. environments directly. If you want the filter to number the whole block as a whole, use `split`, `aligned` etc. environments in the `equation` environment. In multiline environments, **`\nonumber` commands are supported** to turn off the numbering of a specific line.

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
    d &= e - f \label{eq:align2} \\
    g &= h \nonumber \\
    i &= j + k \label{eq:align3}
\end{align}
```

This equation will be numbered line by line, say, (1.2), (1.3) and (1.4), while the third line will not be numbered.

**NOTE: the pandoc filters have no access to the difference of `align` and `align*` environments.** Therefore, you CANNOT turn off the numbering of a specific `align` environment via the `*` mark. If you do want to turn off the numbering of a specific `align` environment, a temporary solution is to manually add `\nonumber` commands to every line of the environment. *This may be fixed by a custom lua reader to keep those information in the future.*

## List of Figures and Tables

**Currently, this feature is only available for `docx` output with Python>=3.8.**

If you set the metadata `custom-lof` and `custom-lot` to `true`, the filter will generate a custom list of figures and tables.

The captions used in the list of figures and tables are the short captions if they are defined in the LaTeX source code. If not, the full captions are used. The short captions are defined in the LaTeX source code as `\caption[short caption]{full caption}`.

The list of figures and tables will be put at the beginning of the document by default. If you want to put the lists at posistions where the `\listoffigures` and `\listoftables` commands are found in the LaTeX source code, you should pass `-f latex+raw_tex` to the pandoc command. However, currently, **`-f latex+raw_tex` does NOT work if you're using `subfiles` package.**.

## Data Export

If you set the metadata `data-export-path` to a path, the filter will export the filter data to the specified path in the JSON format. This is useful for further usage of the filter data in other scripts or filter debugging. The output data is a dictionary with identifiers (labels) as keys and the corresponding data as values. The info dict contains the following keys: `nums: list[int]`, `item_type: Literal["fig", "tab", "eq", "sec", "subfig"]`, `caption: Optional[str]`, `short_caption: Optional[str]`, `src: str`, `ref: str`, `cref: str`, `Cref: str`.

## Log

Some warning message will be shown in the log file named `pandoc-tex-numbering.log` in the same directory as the output file. You can check this file if you encounter any problems or report those messages in the issues.


## `org` file support

`org` files are supported by adding an additional lua filter `src\org_helper.lua` to the pandoc command. The usage is as follows:

```bash
pandoc --lua-filter org_helper.lua --filter pandoc-tex-numbering input.org -o output.docx
```

**Be sure to use `--lua-filter org_helper.lua` before `--filter pandoc-tex-numbering`**.

Reason for this is the default `org` reader of `pandoc` does not parse LaTeX codes by default, for example, LaTeX equations in `equation` environments and cross references via `\ref{}` macros are parsed as `RawBlock` and `RawInline` nodes, while we desire `Math` nodes and `Link` nodes respectively. The `org_helper.lua` filter helps read these blocks via `latex` reader and after that, the `pandoc-tex-numbering` filter can work as expected.

Related discussions can also be found in [pandoc issue #1764](https://github.com/jgm/pandoc/issues/1764) (codes in `org_helper.lua` are based on comments from @tarleb in this issue) and [pandoc-tex-numbering issue #1](https://github.com/fncokg/pandoc-tex-numbering/issues/1).

# Examples

With the testing file `tests/test.tex`:

## Default Metadata

```bash
pandoc -o output.docx -F pandoc-tex-numbering test.tex 
```

The results are shown as follows:

![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/default-page1.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/default-page2.jpg?raw=true)

## Customized Metadata

In the following example, we custom the following **silly** items *only for the purpose of demonstration*:
- Reset the numbering at the second level sections, such that the numbering will be shown as "1.1.1", "3.2.1" etc.
- The formattings are set as follows:
  - For sections:
    - at the beginning of sections, use Chinese numbers "第一章" for the first level sections and English numbers "Section 1.1" for the second level sections.
    - when referred to, use, in turn, "Chapter 1", "第1.1节" etc.
  - For tables:
    - at the beginning of captions, use styles like `Table 1-1-1`
    - when referred to, use styles like `table 1 (in Section 1.1)`
  - For figures:
    - at the beginning of captions, use styles like `Figure 1.1:1`
    - when referred to, use styles like `as shown in Fig. 1.1.1,`
  - For equations, at the end of equations, use styles like `(1-1-1)`
  - For subfigures:
    - use greek letters for symbols
    - at the beginning of captions, use styles like `[β(1)]`
- Turn on custom list of figures and tables and:
  - Use custom titles as "图片目录" and "Table Lists" respectively.
  - Use hyphens as the leader in the lists.
- For multiple references:
  - Stop suppressing the multiple references.
  - Use "、" as the separator between the multiple references.
  - Use " & "(spaces at both ends) as the last separator between the last two references.
- Export the filter data to a file named `data.json`.

Run the following command with corresponding metadata in a `metadata.yaml` file (**recommended**):

```bash
pandoc -o output.docx -F pandoc-tex-numbering --metadata-file test.yaml -f latex+raw_tex test.tex
```

```yaml
# test.yaml
figure-prefix: Fig
table-prefix: Tab
equation-prefix: Eq
number-reset-level: 2
non-arabic-numbers: true
section-src-format-1: "第{h1_zh}章"
section-src-format-2: "Section {h1}.{h2}."
section-cref-format-1: "chapter {h1}"
section-cref-format-2: "第{h1}.{h2}节"
table-src-format: "Table {h1}-{h2}-{tab_id}"
table-cref-format: "table {tab_id} (in Section {h1}.{h2})"
figure-src-format: "Figure {h1}.{h2}:{fig_id}"
figure-cref-format: "as shown in Fig. {num}"
equation-src-format: "\\qquad({h1}-{h2}-{eq_id})"
subfigure-src-format: "[{subfig_sym}({subfig_id})]"
subfigure-symbols: "αβγδεζηθικλμνξοπρστυφχψω"
custom-lot: true
custom-lof: true
lot-title: "Table List"
lof-title: "图片目录"
list-leader-type: "hyphen"
data-export-path: "data.json"
multiple-ref-suppress: false
multiple-ref-separator: "、"
multiple-ref-last-separator: "\\ &\\ "
```

The results are shown as follows:
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page1.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page2.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page3.jpg?raw=true)

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

## Advanced docx Support

In `oxml.py`, I added a built-in framework to support high-level OOXML operations. If you're familiar with OOXML, you can utilize this framework to embed OOXML codes directly into the output (into `RawBlock` nodes with `openxml` format).

# FAQ

- **Q: Can the filter work with xxx package?**
- **A**: It depends. If the package is supported by pandoc, then it should work. If not, you may need to a custom filter or reader to parse the LaTeX codes correctly. In the latter case, this is out of the scope of this filter. For example, the macro `\ce` in the `mhchem` package is not supported by pandoc, so we cannot parse the chemical equations correctly.
- **Q: Can the filter support complex caption macros such as `\bicaption`?**
- **A**: No for now. Caption macros such as `\bicaption` are not supported by the default `latex` reader of pandoc. Therefore, we cannot parse them correctly. You may need a custom reader to parse them correctly or modify the source code before using this filter.
- **Q: Can `docx` output support the short captions in the list of figures and tables?**
- **A**: Now supported.

That said, however, functionalities mentioned above can never be supported easily since they are not, and maybe never will be, supported by native `pandoc` framework.

# TODO

There are some known issues and possible improvements:
- [x] Support multiple references in `cleveref` package.
- [x] Add empty caption for figures and tables without captions (currently, they have no caption and therefore links to them cannot be located).
- [ ] Directly support `align*` and other non-numbered environments.
- [x] Subfigure support.
- [x] Support short captions in `docx` output.
- [ ] Support right-aligned equation numbers.