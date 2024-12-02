# pandoc-tex-numbering
With `pandoc-tex-numbering`, you can convert your LaTeX source codes to any format pandoc supported, especially `.docx`, while **keep all your auto-numberings and cross references**. `pandoc-tex-numbering` even supports **multi-line environments** in LaTeX math block such as `align`, `cases` etc.

# Installation

1. Install `pandoc` and `python3` if you haven't.
2. Install python package `panflute` and `pylatexenc` if you haven't:
    ```bash
    pip install panflute pylatexenc
    ```
3. Download the `pandoc-tex-numbering.py` and put it in your PATH or in the same directory as your LaTeX source file.

# Usage

Take `.docx` as an example:

```bash
pandoc --filter pandoc-tex-numbering.py input.tex -o output.docx
```

# Details

## Figures and Tables

All the figures and tables are supported. All references to figures and tables are replaced by their numbers, and all the captions are added prefixs such as "Figure 1.1: ".

## Equations

Single-line equations are auto-numbered. At the end of every equation, a label is added such as `(1.1)`.

Multi-line equations are:

- numbered for each line if there's at least one `\label{}` command inside the environment.
- numbered for the whole block if there's no `\label{}` command inside the environment.

Therefore, if you want to reference a multi-line equation as a whole, you should put a `\label{}` command outside the environment. While if you want to reference a specific line, you should put a `\label{}` command at the corresponding line.

# Examples

With the testing file `testing_data/test.tex`, you can run:

```bash
pandoc --filter pandoc-tex-numbering.py testing_data/test.tex -o testing_data/test.docx
```

The results are shown as follows:

![alt text](https://github.com/fncokg/pandoc-tex-numbering/images/output-page1.jpg?raw=true)
![alt text](https://github.com/fncokg/pandoc-tex-numbering/images/output-page2.jpg?raw=true)