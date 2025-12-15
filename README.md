# LaTeX-Doctor
LaTeXDoctor is a lightweight utility toolkit designed to analyze, clean, and improve LaTeX documents, with a strong focus on PhD theses and academic writing.

## Usage

If you want to extract acronyms with definitions, use the following command:
```bash
python main.py --folder data/Manuscript/chapters --export-latex accro.tex
```

```tex
# output:
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
# output:
\chapter{Acronyms}\label{cha:acronyme}
\begin{itemize}
\item \textbf{ACS}
\item \textbf{ANN}
\item \textbf{ANT}
\item \textbf{API}
\item \textbf{CAM}
```