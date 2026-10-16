# Submission checklist: *Journal of Asian Economics* (Elsevier)

The journal's guide for authors could not be opened from the build container
(HTTP 403), so check each item below against the current guide before submitting.

- [x] **Author details**: Lian Cataytay, University of Southeastern Philippines (title-page footnote).
- [x] **Highlights**: `paper/highlights.docx`, 5 bullets of at most 85 characters each (Elsevier's usual rule; confirm).
- [x] **Cover letter**: `paper/cover_letter.docx` (draft; read and adjust).
- [ ] **Guide for authors**: check the word limit, abstract length (currently about 220 words),
      number of keywords (currently 6), JEL codes, reference style, and whether review is
      double-anonymized. If it is, remove the author name and footnote from the manuscript
      and submit a separate title page.
- [ ] **Robustness**: confirm that all seven checks (including the expanding window) are in
      `output/tables/accuracy.csv` and that Section 6 reads correctly.
- [ ] **References flagged as unverified**: `ke2017` (LightGBM; no DOI) and the pages of `atkeson2001`.
- [ ] **Reference paper**: the PDF of Medeiros et al. (2021) was not available, so the replication
      gate is qualitative. The manuscript says so in the Limitations paragraph.
- [ ] **Data and code statement**: deposit the repository (e.g. a Zenodo DOI) and cite it.
- [ ] **Pre-registration evidence**: cite the commit hashes of the pre-registration (`git log`).
- [ ] **Final read-through** in Word, with true Times New Roman; check that equation (1) shows parentheses.
