# Copilot Instructions for Application Setup

## Overview
This codebase automates job application document generation using Python, XML parameters, and LaTeX templates. It clones a template repository for each application, generates personalized LaTeX files, builds PDFs, and prepares emails with attachments.

## Architecture
- **Parameter Management**: `parameters.xml` defines application details (receiver info, position, URLs) using LaTeX `\newcommand` syntax.
- **Application Structure**: Each application lives in `applications/YYYYMMDD NN - Company/` with subdirs: `Bewerbung/` (LaTeX docs), `E-Mail/` (email drafts), `Stellenanzeige/` (job listings).
- **Template Cloning**: New applications clone from `https://github.com/MBanucu/application.git` and apply patches from `patches/`.
- **PDF Generation**: LaTeX builds create application PDFs; job listings are scraped as PDFs from URLs.
- **Email Integration**: Thunderbird composes emails with HTML bodies and PDF attachments.

## Key Workflows
- **Create New Application**: Edit `parameters.xml`, run `./newApplication.sh` (clones repo, generates `parameters.tex`, builds PDF, opens email composer).
- **Update CSV Tracker**: Run `python writeCSV.py` to merge application data from `Liste Bewerbungen.csv` into `generated application list.csv`.
- **Patch Templates**: Place modified files in `patches/` mirroring the cloned structure (e.g., `patches/Bewerbung/` overwrites cloned `Bewerbung/`).

## Conventions
- **XML Parameters**: Use `\newcommand{\macroName}{value}` for LaTeX macros; escape `&`, `%`, `#` in `newApplication.py`.
- **Directory Naming**: `YYYYMMDD NN - Company` (e.g., `20251124 01 - Computer Futures`).
- **Language Handling**: Support "German" and "English" for emails and PDF names (see `getEmailSubject()`, `getAnrede()` in `newApplication.py`).
- **Gender Adaptation**: "Mr", "Mrs", or empty in `adaptGender` command.
- **Font Setup**: Nix shell installs URW Arial if missing via `shellHook`.

## Dependencies
- Python packages: `pytz`, `weasyprint`, `pandas`.
- System tools: `texliveFull`, `pdftk`, `wget`, `thunderbird`.
- Use `shell.nix` for reproducible environment.