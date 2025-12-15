# LaTeX-Doctor
LaTeXDoctor is a lightweight utility toolkit designed to analyze, clean, and improve LaTeX documents, with a strong focus on PhD theses and academic writing.

## Usage

### Extract Acronyms

To extract acronyms from your LaTeX files, use the `--task acronyms` option.

If you want to extract acronyms with definitions, use the following command:
```bash
python main.py --folder data/Manuscript/chapters --export-latex accro.tex
```

```tex
% output:
\chapter{Acronyms}\label{cha:acronyme}
\begin{itemize}
\item \textbf{ACS:} Attribution Concordance Score
\item \textbf{ANN:} Artificial Neural Network
\item \textbf{ANT:} Archives Of Tunisia
\item \textbf{API:} Application Programming Interface
\item \textbf{CAM:} Class Activation Maps
```
If you want only want to extract acronyms without definitions, use the `--no-definitions` option:

```bash
python main.py --folder data/Manuscript/chapters --export-latex accro.tex --no-definitions
```
```tex
% output:
\chapter{Acronyms}\label{cha:acronyme}
\begin{itemize}
\item \textbf{ACS}
\item \textbf{ANN}
\item \textbf{ANT}
\item \textbf{API}
\item \textbf{CAM}
```

## Standardize Titles

You can standardize the titles (chapters, sections, etc.) in your LaTeX files using the `--task titles` option.

### Modes
- `Uppercase` (Default): Converts titles to Title Case (standard capitalization).
- `Capitalize`: Converts titles to Sentence case (first letter uppercase, rest lowercase).
- `AllCaps`: Converts titles to ALL CAPS.

### Usage

To standardize titles in a single file to Title Case (default) and save to `output/` folder:
```bash
python main.py --file main.tex --task titles
```

To standardize titles in a folder using Sentence Case:
```bash
python main.py --folder chapters --task titles --title-standard Capitalize
```

To modify files **in-place** (overwrite original files):
```bash
python main.py --folder chapters --task titles --inplace
```