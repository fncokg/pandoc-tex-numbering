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





