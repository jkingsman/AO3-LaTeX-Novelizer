# AO3 LaTeX Novelizer

This tool allows a list of AO3 works to be compiled into novel form via LaTeX and then to PDF.

Please note that this tool is only intended to work on plain HTML AO3 exports; no guarantees are made as to compatibility with image-heavy or custom-styled fics.

This tool runs best on *nix systems such as Linux or Mac OS. This tool has not been tested on Windows.

# Loading AO3 Exports

0. Place regular AO3 "Download" -> "HTML" exports into the `html_exports` directory.
1. Ensure you have a modern (3.10+) `python` installation and `pandoc` on your path. This tool was developed for `pandoc` 3.4, but should work with most versions.
2. Run the script to invoke `pandoc` and perform a bulk conversion of your exported HTML into LaTeX, adding them into the `latex_source` LaTeX project. Note that you need to prefix the script with environment variables to describe your work! These are:
    * `NOVELIZER_AUTHORNAME`
    * `NOVELIZER_BOOKTITLE`
    * `NOVELIZER_SUBTITLE`
    * `NOVELIZER_YEAR`
    * `NOVELIZER_COPYRIGHT` (optional; additional text to go in `copyrightpage.tex`)

    For example, a full invocation may look like
    ```bash
    NOVELIZER_AUTHORNAME="Eliza Smith" NOVELIZER_BOOKTITLE="Collected Works" NOVELIZER_SUBTITLE="AO3 Follies" NOVELIZER_YEAR="1984" ./compile_exports.py
    ```

    When you run the script, you should see descriptive output as it works through each step.

If you want to reorder the works, open `latex_source/main.tex` after running the `compile_exports` script and move around the `\input{}` directives after `%% FILE CONTENTS START %%`.

## Next Steps

*Note that this outputs a complete LaTeX project in the `latex_source` directory and does not actually generate a complete PDF!*

In order to convert to PDF, you can use a website like Overleaf to upload a ZIP file containing the `latex_source` directory.

If you want to build locally, you'll need a LaTeX program capable of PDF output. Finding, installing, and using those is beyond the scope of this README, I'm sorry.

If you want to customize the size and format for binding, you can find those settings in `options.sty`.

Please pay attention to compilation warnings; as-is, you'll likely need some manual character shimming for anything non-ASCII in PDFTeX. You may want to use XeLaTeX for better Unicode compatibility.

## Experimental Flags
You may set these experimental environment variables.

`STRIP_NOTES`: strip out summaries and notes. Experimental and janky.

`CONVERT_VERBATIM`: convert `\begin{verbatim}` blocks into `\begin{lstlisting}` blocks to prevent line-break (or lack thereof) issues with `<code>` blocks converted to the non-wrapping `verbatim`.

e.g. `[...] STRIP_NOTES=y CONVERT_VERBATIM=y ./compile_exports.py`


## Example Invocation

```bash
export NOVELIZER_AUTHORNAME="Da Great Author"
export NOVELIZER_BOOKTITLE="Collected Words"
export NOVELIZER_SUBTITLE="AO3 Works, 2014-2018"
export NOVELIZER_YEAR="2024"
export NOVELIZER_COPYRIGHT="The author disclaims all copyright."
export STRIP_NOTES=y # if you don't want summaries or author's notes
export CONVERT_VERBATIM=y # if you have blocks of <code> that you want to line wrap instead of run off the page
./compile_exports.py
```

If you had `XeLaTeX` installed, you might then run

```bash
cd latex_source/

# run as many times as you have to for XeLaTeX to converge on layout, generate a ToC, etc.
xelatex.exe -synctex=1 -interaction=nonstopmode main.tex
xelatex.exe -synctex=1 -interaction=nonstopmode main.tex
xelatex.exe -synctex=1 -interaction=nonstopmode main.tex
xelatex.exe -synctex=1 -interaction=nonstopmode main.tex
xelatex.exe -synctex=1 -interaction=nonstopmode main.tex
```

And then retrieve `main.pdf`.

# What about non-AO3 HTML?
Generally, this tool is specifically meant to work on AO3 HTML exports, but there's technically not a reason it can't work on other HTML -- as long as Pandoc can eat it, it should convert. You may get errors about not finding chapter titles; any manipulation of the generic output will be up to you in terms of establishing a chapter structure from Pandoc's file fragments.

# Licensing

This codebase uses the `Memoir Book Template (6x9 default)` by Vellichor Dreams, licensed under [LaTeX Project Public License 1.3c](https://www.latex-project.org/lppl/lppl-1-3c/). Modifications to template are made with license compliance.

Original components of this codebase, including documentation and Python scripts, are released under MIT license, copyright 2024 Jack Kingsman <jack@jackkingsman.me> or <jack.kingsman@gmail.com>. See LICENSE.md for more information.
