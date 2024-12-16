# pandoc-tex-numbering
This is an all-in-one pandoc filter especially for LaTeX files to keep **numbering, hyperlinks, caption prefixs and cross references in (maybe multi-line) equations, sections, figures, and tables**.

With `pandoc-tex-numbering`, you can convert your LaTeX source codes to any format pandoc supported, especially `.docx`, while **keep all your auto-numberings and cross references**. 

`pandoc-tex-numbering` even supports **multi-line environments** in LaTeX math block such as `align`, `cases` etc.

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

Note: By default, the filter will number the sections, figures, tables, and equations. In case you only want to number some of them (for example in case you want to number only equations with this filter while number others with other filters), you can set the corresponding variables in the metadata of your LaTeX file. See the [Customization](#customization) section for more details.

## Customization

You can set the following variables in the metadata of your LaTeX file to customize the behavior of the filter:

### General
- `number-figures`: Whether to number the figures. Default is `True`.
- `number-tables`: Whether to number the tables. Default is `True`.
- `number-equations`: Whether to number the equations. Default is `True`.
- `number-sections`: Whether to number the sections. Default is `True`.
- `number-reset-level`: The level of the section that will reset the numbering. Default is 1. For example, if the value is 2, the numbering will be reset at every second-level section and shown as "1.1.1", "3.2.1" etc.

### Figures
- `figure-prefix`: The prefix of the caption of figures. Default is "Figure".

### Tables
- `table-prefix`: The prefix of the caption of tables. Default is "Table".

### Sections
- `section-format-1`,`section-format-2`,...: The format of the section numbering at each level.

You can use python f-string format to customize the numbering format. The numbers of each level headers are available as fields `h1`,...,`h10`. The default values of `section-format-3` is `{h1}.{h2}.{h3}`, for example.

You can do this trick:

```command
pandoc --filter pandoc-tex-numbering.py -M section-format-1="Chapter {h1}." -M section-format-2="Section {h1}.{h2}." input.tex -o output.docx
```

With these metadata (i.e. `section-format-1` set to "Chapter {h1}." and `section-format-2` set to "Section {h1}.{h2}."), the first-level section will be numbered as "Chapter 1.", "Chapter 2." etc., and the second-level section will be numbered as "Section 1.1.", "Section 1.2." etc. (By default, the first-level section is numbered as "1", "2" etc., and the second-level section is numbered as "1.1", "1.2" etc.)

# Details

## Figures and Tables

All the figures and tables are supported. All references to figures and tables are replaced by their numbers, and all the captions are added prefixs such as "Figure 1.1: ".

You can determine the prefix of figures and tables by changing the variables `figure-prefix` and `table-prefix` in the metadata, default values are "Figure" and "Table" respectively.

## Equations

Equations under multiline environments such as `align`, `cases` etc. are numbered line by line, and the others are numbered as a whole block.

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

In the following example, we only want to set the prefix of figures and tables as "Fig" and "Tab" respectively and reset all the numbering at the second-level section. We also want to set the format of the first-level section as "Chapter 1.", "Chapter 2." etc.

```bash
pandoc -o output.docx -F pandoc-tex-numbering.py -M figure-prefix="Fig" -M table-prefix="Tab" -M number-reset-level=2 -M section-format-1="Chapter {h1}." test.tex
```

Note: It is recommended to set metadata in a separate `.yaml` file rather than in the command line. The command line is only for demonstration.

The results are shown as follows:
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page1.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/blob/main/images/custom-page2.jpg?raw=true)

# Development

If you want to modify the filter, you can modify the `pandoc-tex-numbering.py` directly. The filter is written in Python and based on `panflute`.

## Modify Configuration

Some configurations have not coded as metadata yet, but you can easily edit them in the python code. For example, you can add new environment names to `doc.pandoc_tex_numbering:"multiline_envs"` to support more multiline environments.

## Extend the Filter

The logical structure of the filter is quiet straightforward. You can see this filter as a scaffold for your own filter. For example, `_parse_multiline_environment` function receives a latex math node and the doc object and returns a new modified math string with the numbering and respective labels. You can add your customized latex syntax analysis logic to support more complicated circumstances.

It is recommended to decalre all your possible variables in the `prepare` function, and save them in the `doc.pandoc_tex_numbering:dict` object. This object will be automatically destroyed after the filter is executed.

