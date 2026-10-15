"""Example: the Agbola and Acupan (2010) critical review deck in the Lian signature style.

Run:  python3 example_deck.py [out.pptx]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lian_deck import Deck  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("example_deck.pptx")

d = Deck(short_title="Critical review · Agbola and Acupan (2010)")

d.title_slide(
    "Critical Review: An Empirical Analysis of International Labour Migration in the Philippines",
    ["Agbola, F. W. & Acupan, A. B. (2010)", "*Economic Systems*, 34, 386–396"],
    byline="Prepared by: **Lian Cataytay**",
)

s = d.slide("The article at a glance", "The study asks which push factors in the Philippines lead Filipinos to emigrate.")
left, right = d.columns(2)
d.text(s, left, [
    "**8.2 million** Filipinos live or work in more than 193 countries",
    "**US$14.4 billion** in remittances (money sent home) in 2007",
    "The Philippines has the **third-largest diaspora** in the world",
    "Emigration is now a **permanent part** of the economy",
], heading="Why it matters")
d.panel(s, right, [
    "**Authors:** Frank W. Agbola and Angelito B. Acupan",
    "**Journal:** *Economic Systems* (Elsevier), 2010",
    "**Data:** yearly national data, 1975–2005 (31 years)",
    "**Method:** error correction model (ECM)",
    "**Type:** quantitative, time-series study",
], heading="About the article", bullets=False)

s = d.slide("Key terms used in this review", "Each term keeps the same meaning on every slide.")
d.table(s, d.body(), [
    ["Term", "Meaning"],
    ["Emigration", "People leaving the Philippines to live or work abroad"],
    ["Migration share", "Filipino migrants as a share of the population; what the study explains"],
    ["Push / pull factor", "A condition at home that pushes people out / a condition abroad that pulls them in"],
    ["Proxy", "A stand-in measure for something that cannot be measured directly"],
    ["Stationary", "Data that move around a stable average; checked with a unit root test"],
    ["Cointegration", "Data series that drift over time but still move together in the long run"],
    ["ECM and ECT", "Error correction model; its error correction term shows how fast data return to the long-run path"],
    ["Statistically significant", "Unlikely to be due to chance (here, at the 5% level)"],
], col_widths=[1, 3.2], first_col_bold=True, size=16)

s = d.slide("1. Research problem and gap", "Emigration became permanent, but its causes were “not well established.”")
top, bottom = d.split(d.body(), 1.0)
left, right = d.columns(2, top)
d.text(s, left, [
    "In the 1970s, sending workers abroad began as a **short-term fix** for unemployment",
    "It became a **permanent part** of the economy",
    "The law is **unclear**: RA 8042 says the State “does not promote” overseas work, but deployment “shall be encouraged”",
], heading="The problem")
d.text(s, right, [
    "The causes of emigration from the Philippines are **not well established**",
    "Policymakers need **evidence** on which push factors matter most",
], heading="The gap")
d.callout(s, bottom, "Research question:", "How do economic, demographic and political factors affect emigration from the Philippines?")

s = d.slide("2. Theoretical framework", "The authors combine four theories into one model of push factors.")
top, bottom = d.split(d.body(), 0.9)
left, right = d.columns(2, top, widths=[1.4, 1])
d.text(s, left, [
    "**Ravenstein (1885); Todaro (1969):** people migrate when they expect a better life abroad",
    "**Human capital theory (Hicks 1939):** migration is an investment; more educated people migrate more",
    "**Roy effect (Borjas 1987):** income inequality decides which skill groups leave",
    "**Gravity model (Greenwood 1975):** migration depends on income, population and the cost of migration",
], numbered=True)
d.panel(s, right, [
    "**Migration share** = *f*(cost of migration, adult literacy, income inequality, income inequality^{2}, "
    "political instability, inflation, population density, unemployment, per capita income)",
], heading="The model in words", bullets=False)
d.callout(s, bottom, "Critical view:", "a mix of theories, not one model. Only push factors are used; pull factors from destination countries are left out.")

s = d.slide("3. Data", "Yearly national data, 1975–2005: only 31 observations, all secondary data.")
top, bottom = d.split(d.body(), 0.8)
d.table(s, top, [
    ["Variable", "Measure / proxy", "Source", "Exp. sign"],
    ["Migration share", "Migrants (temporary + permanent) ÷ population", "CFO; NSCB", "Explained"],
    ["Cost of migration", "Average one-way airfare, Manila → top 24 destinations (proxy)", "Authors’ estimate", "−"],
    ["Adult literacy", "Adult literacy rate (proxy for education)", "BSP; NSCB", "+"],
    ["Income inequality, inequality^{2}", "Gini coefficient and its square (Roy effect)", "Not stated", "±"],
    ["Political instability", "Number of leadership changes, coups and uprisings", "Gastil (1987)", "−"],
    ["Inflation", "Inflation rate (consumer prices)", "IMF; BSP; NSCB", "−"],
    ["Population density", "People per km^{2}", "NSCB", "+"],
    ["Unemployment", "Unemployment rate", "IMF; BSP; NSCB", "+"],
    ["Per capita income", "Real GDP per person", "IMF; BSP; NSCB", "−"],
], col_widths=[1.5, 3, 1.3, 0.8], align=["l", "l", "l", "c"], size=14)
d.callout(s, bottom, "Critical view:", "the source of the income inequality data is not stated, and the migration share mixes temporary and permanent migrants.")

s = d.slide("4. Methodology", "A standard five-step time-series method, carefully applied.")
top, bottom = d.split(d.body(), 0.8)
d.text(s, top, [
    "**Unit root tests:** ADF and P–P tests show the data become stationary after first differences",
    "**Cointegration tests:** Engle–Granger, Johansen and Pesaran tests show the variables move together in the long run",
    "**Choosing the model:** general-to-specific; drop terms that are not statistically significant",
    "**Estimation:** the ECM is estimated by ordinary least squares (OLS) in EViews 6.0",
    "**Diagnostic tests:** checks for problems in the model; all passed",
], numbered=True)
d.callout(s, bottom, "Watch-out:", "the Johansen test finds 5–8 long-run relationships, but the ECM keeps only one ECT.")

s = d.slide("5. Key findings: the results", "Four push factors are statistically significant; the model explains 63% of changes.")
top, bottom = d.split(d.body(), 0.45)
d.table(s, top, [
    ["Explanatory variable", "Coefficient", "*t*-statistic", "Result (5% level)"],
    ["Unemployment", "+0.236", "4.629", "**Significant**"],
    ["Adult literacy", "−0.659", "−5.225", "**Significant**"],
    ["Political instability", "−0.482", "−3.444", "**Significant**"],
    ["Population density", "−0.254", "−2.756", "**Significant**"],
    ["Income inequality", "−171.195", "−1.594", "Not significant"],
    ["Income inequality^{2}", "+165.927", "1.323", "Not significant"],
    ["Inflation", "−0.036", "−1.327", "Not significant"],
    ["Cost of migration", "−0.002", "−0.429", "Not significant"],
    ["Per capita income", "−0.0002", "−0.293", "Not significant"],
], col_widths=[2, 1, 1, 1.4], align=["l", "r", "r", "l"], size=14)
d.text(s, bottom, ["**Model fit:** adjusted R^{2} = 0.63  ·  ECT = −0.776 (78% of any gap closes within a year)  ·  F-statistic = 5.848 (*p* = 0.000)"], bullets=False, size=15)
d.source(s, "Source: Agbola and Acupan (2010), Table 4.")

s = d.slide("5. Key findings: four significant push factors", "Unemployment raises emigration; three other push factors lower it.")
cells = d.grid(2, 2)
for box, head, body in zip(cells, [
    "Unemployment ↑ → emigration ↑", "Adult literacy ↑ → emigration ↓",
    "Political instability ↑ → emigration ↓", "Population density ↑ → emigration ↓"], [
    "Coefficient +0.236. Emigration is a “safety valve” when there are not enough jobs.",
    "Coefficient −0.659. The opposite of human capital theory. The authors say most migrants do low-skilled jobs.",
    "Coefficient −0.482. The migration share fell in unstable years (1983, 1986, 2001, 2005).",
    "Coefficient −0.254. The opposite of what was expected; the authors cannot fully explain it."]):
    d.panel(s, box, [body], heading=head, bullets=False)

s = d.slide("5. Key findings: other results and conclusions", "Income, inflation, migration cost and inequality do not significantly affect emigration.")
left, right = d.columns(2)
d.panel(s, left, [
    "**Cost of migration** and **per capita income**: negative, as expected",
    "**Inflation**: negative, as expected",
    "**Income inequality** and **income inequality^{2}**: the Roy effect does not hold for the Philippines",
], heading="Not statistically significant")
d.panel(s, right, [
    "**Main push factors:** unemployment, adult literacy, political instability, population density",
    "**Collect and track** migration data better",
    "**Sign agreements** with destination countries to protect overseas Filipino workers",
    "**Build a home economy** with enough jobs, so the country relies less on emigration",
], heading="The authors’ conclusions")

s = d.slide("Critical assessment of the study", "Careful methods, but a small sample, weak proxies and missing pull factors.")
left, right = d.columns(2, widths=[1, 1.25])
d.text(s, left, [
    "**Important question** for a country that sends many workers abroad",
    "**Careful steps:** unit root tests, cointegration tests, then the ECM",
    "**All diagnostic tests** reported and passed",
    "**Clear policy background** (RA 8042)",
], heading="Strengths")
d.text(s, right, [
    "**Small sample:** 31 yearly observations for 10 explanatory terms",
    "**Weak proxies:** airfare for cost of migration; adult literacy for education",
    "**Push factors only:** pull factors from destination countries are missing",
    "**Conflicting explanation:** “low-skilled migrants” clashes with data the paper cites on professionals leaving",
    "**Unclear tests:** per capita income is not stationary in the P–P test; no tests for structural breaks",
], heading="Weaknesses")

s = d.slide("6. Limitations and areas for further research", "Better data and pull factors are the next steps.")
left, right = d.columns(2)
d.panel(s, left, [
    "Migration data are **hard to collect** and compile",
    "Airfare shows only the **minimum cost** of migration",
    "The **population density** result is hard to explain",
    "The data **cannot prove** the political instability story",
], heading="Limitations the authors identify")
d.panel(s, right, [
    "**Split the data:** temporary vs. permanent migrants, and by skill level",
    "**Add pull factors:** wages and job demand in destination countries",
    "**Update the data:** go past 2005 and test structural breaks (1997, 2008, COVID-19)",
    "**Use household data:** test human capital theory with survey data on migrants",
], heading="Future research (my suggestions)", numbered=True)

d.takeaway("Push factors at home shape Filipino emigration.", [
    "**Unemployment raises emigration;** adult literacy, political instability and population density lower it",
    "**Policy message:** build a home economy with enough jobs",
    "**Read with care:** small sample, weak proxies and missing pull factors",
])
d.closing()
d.save(OUT)
