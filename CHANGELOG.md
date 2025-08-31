# 1.3.3 (2025-08-31)
Fix some bugs:

- Fix #19 : multiline equations with `\nonumber` commands are not numbered correctly.
- Fix #17 : Python<=3.8 compatibility issue caused by type annotations.
- Fix the bug that the `gather` environment is not numbered correctly (see #18)
- Explicitly note in documentation that the we do not fully support `aligned` and `gathered` currently.

# 1.3.2 (2025-07-26)
Support specifying the multiple reference style in the metadata, so that you can get "equation 1, equation 2 and equation 3" instead of "equations 1, 2 and 3" in the multiple references.

Fix some bugs:
- Fix the bug that files containing levels beyond `max_level` cause crash.
- Fix the bug that the `\label` command outside the `\section` command is not processed correctly.

# 1.3.1 (2025-04-12)
Support specifying the numbering offset of any type of numbering.

Some minor bug fixes and improvements:
- Remove the `\listoffigures` and `\listoftables` command searching process, such that the feature of customizable lot/lof location is no longer supported. This is because: to enable latex command searching, we need to a `raw_tex` input, which in many cases will lead much more errors.
- Remove some typing for the backward compatibility consideration.

# 1.3.0 (2025-03-26)
Support various custom numbering styles in a more clear and flexible way:
- support various and auto-extend numbering symbols: arabic numbers, roman numbers, latin/greek/cyrillic letters (both upper and lower case), Chinese numbers, etc.
- support custom numbering symbols for anything: any level of section, figure, table, equation, theorem, etc.

Support appendix numbering.

Metadata `{item_type}-symbols` and fields `{item_type}_sym` are no longer supported.

## Migration Guide
For people who are using 1.2.x version, there are some **removals**:

The following metadata keys have already marked as deprecated in the previous version, and they are now **removed**:
- metadata keys `section-format-source-i` and `section-format-ref-i` for the i-the level section numbering formatting are now removed. You should use the new `section-src-format-i` and `section-cref-format-i` keys instead.

The following features are now **removed**, and you should use the new API instead:
- metadata keys `{item_type}-symbols` and formatting fields `{item_type}_sym` are now removed. Now you can simply use `{item_type}-numstyle` to specify the numbering style directly.

# 1.2.5 (2025-03-13)
Support theorem numbering. Also refer to a [StackExchange question](https://tex.stackexchange.com/questions/738132/simultaneously-cross-referencing-numbered-amsthm-theorems-and-numbered-equations).

# 1.2.4 (2025-03-07)
Support customizable spacing command in the `equation-src-format` field (default now is `"\\quad({num})"`). Also refer to issue #11.

# 1.2.3 (2025-02-01)
Fix type casting problem when inputting the metadata from the command line. 

Announce stable status in the project classifiers.

# 1.2.2 (2025-01-15)

Support multiple references in the same ref command, such as \cref{fig1,fig2,fig3}.

# 1.2.1 (2025-01-13)

Fix a severe numbering logic bug in the previous version. Now the numbering system should work as expected.

# 1.2.0 (2025-01-13)

Rewrite the low-level numbering system (switch to a OOP design). Now we support:

- Full-featured formatting for the numbering system
- OOP designed API for the numbering system, which is much easier to extend

## Migration Guide
For people who are using 1.1.x version, there are some **deprecations** and **removals**:

The following metadata keys are now deprecated, and you are recommended to use the new keys instead (the old keys are still supported until v1.3.0):
- metadata keys `section-format-source-i` and `section-format-ref-i` for the i-the level section numbering formatting are now deprecated. You should use the new `section-src-format-i` and `section-cref-format-i` keys instead. For backward compatibility, the old keys are still supported until the next major release (1.3.0).

The following features are now **removed**, and you should use the new API instead:
- metadata keys `subfigure-format` is now removed considering its ambiguity. You should use the new unified metadata keys `subfigure-src-format` and `subfigure-cref-format` instead.
- fields `num` and `sym` in `subfigure-format` are (of course) now removed. The new fields `subfig_id` and `subfig_sym` should be used instead.

# 1.1.2 (2025-01-08)

Fix #7: support compatibility with python >=3.8

# 1.1.1 (2025-01-07)

Use the correct style name (style id) for list of figures and tables.

# 1.1.0 (2025-01-06)

Custom list of figures and tables supporting **short captions* and custom titles.

# 1.0.3 (2025-01-05)

Add OXML base support for future docx development.


# 1.0.2 (2025-01-05)

Fix import error in the `pandoc_tex_numbering/__init__.py` file.

# 1.0.1 (2025-01-05)

Update the README file to include the installation guide and the usage of the project.

# 1.0.0 (2025-01-05)
After several bug fixes and improvements, I released the first stable version of the project. 

## Migration Guide
For people who are using the beta version, there are some minor changes:
- It is recommended to install the project via pip now.
- You're now **NOT** required to put the files under the same directory of your project: after installing the project via pip, you can use the command like `pandoc -o test.docx -F pandoc-tex-numbering test.tex` (with no suffix `.py`).
- The old `non-arabic-number` metadata is now deprecated. It is now turned on at any time.
- For people who want to use the `org` format, you still need to download the `org_helper.lua` file manually and put it under the same directory of your project (It is now located at `src/org_helper.lua`).





