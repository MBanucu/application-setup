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

## Guidance: Filling `parameters.xml` from a Job Listing (workflow)

Use this workflow when you receive a new job listing (URL or pasted contact block). The goal is to populate `parameters.xml` reliably so `./newApplication.sh` can generate the application.

1) Start: gather the job listing URL and copy the contact block from current chat. Example start block from chat:

```
https://www.arbeitsagentur.de/jobsuche/jobdetail/10001-1001807019-S

Informationen zur Bewerbung
Kontaktadresse
FUNKE Service GmbH
Herr Emir Can Uzun
Flughafenstraße 2-4
44309 Dortmund

Telefon: +49 231 2868080

E-Mail: bewerbung@funke-service.com
```

2) Primary update: open `parameters.xml` and update these fields:
- `\prenameReceiver` / `\surnameReceiver` — receiver name (from the contact block or the job page)
- `\companyReceiver` — company name
- `\addressStreetReceiver`, `\addressPLZReceiver`, `\addressPlaceReceiver` — street, postal code, city
- `\emailReceiver` — comma-separated list of emails (see step 4 for what to include)
- `\applicationHref` — the job listing URL
- `\applicationPosition` — the job title from the job page (see step 3)
- `\jobAgent` — the person that is communicating between applicant and company for applications (if present)
- `adaptGender` — `Mr`, `Mrs`, or empty depending on the salutation

3) Get the job title: the official position text is on the job listing page. For Arbeitsagentur listings the element id is `detail-kopfbereich-titel`. Use a small curl+sed or your browser to extract it, for example:

```bash
curl -sL 'https://www.arbeitsagentur.de/jobsuche/jobdetail/10001-1001694078-S' \
	| tr '\n' ' ' \
	| sed -n "s/.*id=\"detail-kopfbereich-titel\"[^>]*>\([^<]*\).*/\1/p"
```

Set the exact string returned as `\applicationPosition` (do not escape LaTeX special characters).

4) Collect email addresses: populate `\emailReceiver` with a comma-separated, no-spaces list of:
- the email of the responsible job agent (if given in the posting),
- the central career / careers / jobs email address (if present on the company's careers page),
- the central info / contact email address of the company (from `Impressum` or `Kontakt`).

If an email cannot be found, leave it empty but try to include at least one contact address.

5) If the posting does not include a named responsible person:
- Search the company website for "Bewerbung", "Karriere", "Jobs", or "Recruiting" pages and look for contact persons or HR addresses.
- If still absent, search for "[Company Name] HR" or "[Company Name] Personal" and prefer a direct HR/recruiter email for inclusion.

6) Verification: after editing `parameters.xml` run the build workflow to validate variables and generate the application:

```bash
./newApplication.sh
```

7) Post-processing: update the tracker CSV with the new entry:

```bash
python3 writeCSV.py
```

8) Notes and tips:
- Always escape `&` with `&amp;` and other xml-significant characters before writing them into `parameters.xml`.
- Use the `patches/` directory to stage local template changes that should be applied to the cloned template repository.
- Prefer the official company `Impressum` page for authoritative addresses and general contact emails.
- When adding multiple emails to `\emailReceiver`, separate by commas with no spaces: `a@x.de,b@y.de,c@z.de`.

This workflow is intentionally conservative: add only verified emails and names. If a value is uncertain, leave a short comment in `parameters.xml` for a human reviewer.

## Conventions
- **XML Parameters**: Use `\newcommand{\macroName}{value}` for LaTeX macros.
- **Directory Naming**: `YYYYMMDD NN - Company` (e.g., `20251124 01 - Computer Futures`).
- **Language Handling**: Support "German" and "English" for emails and PDF names (see `getEmailSubject()`, `getAnrede()` in `newApplication.py`).
- **Gender Adaptation**: "Mr", "Mrs", or empty in `adaptGender` command.
- **Font Setup**: Nix shell installs URW Arial if missing via `shellHook`.

## Dependencies
- Python packages: `pytz`, `weasyprint`, `pandas`.
- System tools: `texliveFull`, `pdftk`, `wget`, `thunderbird`.
- Use `shell.nix` for reproducible environment.