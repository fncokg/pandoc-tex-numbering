# 1.0.0 (2025-01-05)
After several bug fixes and improvements, I released the first stable version of the project. 

## Migration Guide
For people who are using the beta version, there are some minor changes:
- It is recommended to install the project via pip now.
- You're now **NOT** required to put the files under the same directory of your project: after installing the project via pip, you can use the command like `pandoc -o test.docx -F pandoc-tex-numbering test.tex` (with no suffix `.py`).
- The old `non-arabic-number` metadata is now deprecated. It is now turned on at any time.
- For people who want to use the `org` format, you still need to download the `org_helper.lua` file manually and put it under the same directory of your project (It is now located at `src/org_helper.lua`).

# 1.0.1 (2025-01-05)

Update the README file to include the installation guide and the usage of the project.

# 1.0.2 (2025-01-05)

Fix import error in the `org_helper.lua` file.