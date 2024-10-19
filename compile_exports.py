#!/usr/bin/env python3

import glob
import os
import re
import shutil
import sys

BASE_LATEX_DIR = "latex_source"
EXPORTS_DIR = "html_exports"
CONTENT_FOLDER = "content"

CONTENT_DIR = os.path.join(BASE_LATEX_DIR, CONTENT_FOLDER)

MAIN_TEX_FILE = os.path.join(BASE_LATEX_DIR, "main.tex")
MAIN_TEX_CONTENTS_START_MARKER = "%% FILE CONTENTS START %%"
MAIN_TEX_CONTENTS_END_MARKER = "%% FILE CONTENTS END %%"

def sanity_check():
    # check pandoc availability
    print("Looking for pandoc...")
    pandoc_path = shutil.which("pandoc")
    if not pandoc_path:
        print("❌ pandoc not found on path! Please install pandoc.")
        sys.exit(1)

    print("✅ Found pandoc. Invoking to dump version...")
    print("=============================================")
    os.system("pandoc --version")
    print("=============================================")

    # check exports dir HTML presence
    print("Checking to see if there are files in exports dir...")
    files_in_exports_dir = glob.glob(os.path.join(EXPORTS_DIR, '*.html'))
    if len(files_in_exports_dir) > 1:
        print(f"✅ Found {len(files_in_exports_dir)} HTML files to convert!")
        print("Files queued for inclusion:")
        for file in files_in_exports_dir:
            print(f"↳ {file}")
    else:
        print("❌ Did not find any *.html files in {EXPORTS_DIR} directory!")
        sys.exit(1)

def dump_html_to_latex():
    print("Beginning file conversion...")
    files_in_exports_dir = glob.glob(os.path.join(EXPORTS_DIR, '*.html'))
    for file in files_in_exports_dir:
        basename = os.path.splitext(file)[0]
        print(f"↳ Converting {file} to {basename}.tex")
        cmd = f"pandoc {file} --output {basename}.tex"
        os.system(cmd)
    print("✅ File conversions complete!")

def append_headers_and_strip_section_redeclaration():
    print("Appending chapter headers to each file, extracted from \\section{} title, then stripping the section title")
    converted_latex_files = glob.glob(os.path.join(EXPORTS_DIR, '*.tex'))
    # capture text inside the section tag up to the label marker (used with DOTALL to account for linebreaks)
    chapter_header = r"\\section{(.*?)}\\label"
    section_redeclaration = r"\\section{.*?by.*?\n\n"
    for latex_file in converted_latex_files:
        print(f"↳ Appending chapter header + stripping section title for {latex_file}")
        with open(latex_file) as latex_handle:
            matches = re.findall(chapter_header, latex_handle.read(), flags=re.DOTALL)
            if len(matches) != 1:
                print(f"❌ Zero or multiple matches extracted for {latex_file} -- I need one and only one title/chapter header. Matches are: '{matches}'")
                print("This file will not have the expected chapter structure.")

        # yay! we got a good capture; reopen the file and write it with the header
        with open(latex_file, 'r') as latex_read_handle:
            substituted_tex_contents = re.sub(section_redeclaration, '', latex_read_handle.read(), flags=re.DOTALL)

            # naughty double handles here! but easy way to prepend our chapter header
            with open(latex_file, 'w') as latex_write_handle:
                latex_write_handle.write(f"\\chapter{{{matches[0]}}}\n" + substituted_tex_contents)

def copy_polished_latex_to_content_dir():
    # copy latex files over to content directory
    # we could just write the updated contents into place but it's neater to get them all out of the exports dir I think
    for latex_file in glob.glob(os.path.join(EXPORTS_DIR, '*.tex')):
        print(f"Copying {latex_file} to {CONTENT_DIR}")
        shutil.copy(latex_file, CONTENT_DIR)

def inject_filenames_into_main_tex():
    file_contents_regex = rf"{MAIN_TEX_CONTENTS_START_MARKER}.*{MAIN_TEX_CONTENTS_END_MARKER}"
    with open(MAIN_TEX_FILE, 'r') as main_tex_read_handle:
        include_list = []
        for latex_file in glob.glob(os.path.join(CONTENT_DIR, '*.tex')):
            # get the work file names with no .tex extension and just the base file name with no path
            no_latex_extension_path = os.path.basename(os.path.splitext(latex_file)[0])
            include_list.append(f"\\input{{{CONTENT_FOLDER}/{no_latex_extension_path}}}")

        newline_joined_include_list = "\n".join(include_list)
        replacement_block = f"{MAIN_TEX_CONTENTS_START_MARKER}\n{newline_joined_include_list}\n{MAIN_TEX_CONTENTS_END_MARKER}"

        # this is a stupid hack with the lambda to prevent python regex from thinking that the backslashes etc. in the tex are RE directives
        substituted_contents_block = re.sub(file_contents_regex, lambda _: replacement_block, main_tex_read_handle.read(), flags=re.DOTALL)

        # more naughty double handles
        with open(MAIN_TEX_FILE, 'w') as latex_write_handle:
            latex_write_handle.write(substituted_contents_block)

def update_copyright_and_authorship_data():
    with open(MAIN_TEX_FILE, 'r') as main_tex_read_handle:
        main_tex_contents = main_tex_read_handle.read()

    author_name = os.environ.get('NOVELIZER_AUTHORNAME', '<no NOVELIZER_AUTHORNAME provided>')
    print(f"Using author name {author_name}")
    main_tex_contents = re.sub('NOVELIZER_AUTHORNAME', author_name, main_tex_contents)

    book_title = os.environ.get('NOVELIZER_BOOKTITLE', '<no NOVELIZER_BOOKTITLE provided>')
    print(f"Using book title {book_title}")
    main_tex_contents = re.sub('NOVELIZER_BOOKTITLE', book_title, main_tex_contents)

    subtitle = os.environ.get('NOVELIZER_SUBTITLE', '<no NOVELIZER_SUBTITLE provided>')
    print(f"Using subtitle {subtitle}")
    main_tex_contents = re.sub('NOVELIZER_SUBTITLE', subtitle, main_tex_contents)

    year = os.environ.get('NOVELIZER_YEAR', '<no NOVELIZER_YEAR provided>')
    print(f"Using year {year}")
    main_tex_contents = re.sub('NOVELIZER_YEAR', year, main_tex_contents)

    # write out the modifications
    with open(MAIN_TEX_FILE, 'w') as latex_write_handle:
        latex_write_handle.write(main_tex_contents)

    copyright_extra = os.environ.get('NOVELIZER_COPYRIGHT', '%% NOVELIZER_COPYRIGHT %%')
    copyright_path = os.path.join(BASE_LATEX_DIR, 'frontmatter', 'copyrightpage.tex')
    with open(copyright_path, 'r') as copyright_tex_read_handle:
        copyright_file_contents = copyright_tex_read_handle.read()
        copyright_file_contents = re.sub(r"%% NOVELIZER_COPYRIGHT %%", lambda _: copyright_extra, copyright_file_contents)
    with open(copyright_path, 'w') as copyright_tex_write_handle:
        copyright_tex_write_handle.write(copyright_file_contents)


if __name__ == '__main__':
    sanity_check()
    dump_html_to_latex()
    append_headers_and_strip_section_redeclaration()
    copy_polished_latex_to_content_dir()
    inject_filenames_into_main_tex()
    update_copyright_and_authorship_data()
