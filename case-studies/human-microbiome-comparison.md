# Statistical Comparison of the Human Microbiome

**Type:** MSc research · **Institution:** Constructor University Bremen · **Completed:** 2024

## Research question

How do microbiome compositions differ between inflammatory bowel disease (IBD) cohorts and controls, and how sensitive are observed differences to the statistical method and level of microbial aggregation?

## Data and workflow

The research used the curatedMetagenomicData Bioconductor ecosystem, including the HMP_2019_ibdmdb relative-abundance dataset. The analysis workflow involved:

1. Inspecting sample metadata and identifying relevant disease groups and sample types.
2. Preparing stool-sample subsets and comparing IBD and control cohorts.
3. Exploring microbial relative-abundance distributions and group-level differences.
4. Applying univariate and multivariate statistical approaches.
5. Interpreting results in the context of compositional microbiome data and methodological limitations.

## Methods explored

- Descriptive summaries and visualisation
- Mann–Whitney and t-test comparisons
- ANOVA
- PERMANOVA and ANOSIM
- Community similarity and network-analysis approaches

## Selected reported results

The analysis reported a PERMANOVA pseudo-F statistic of 19.107081 with p = 0.001. An ANOSIM result was R = -0.010202 with p = 0.767. These results illustrate why conclusions should be tied to the specific distance metric, data preparation and test assumptions rather than reduced to a single claim that groups are different.

## Tools

R, Bioconductor, curatedMetagenomicData, vegan, statistical analysis and data visualisation.

## What this work demonstrates

This research demonstrates experience preparing complex biological datasets, selecting and comparing statistical methods, interpreting multivariate results and communicating limitations.

*This page summarises the research workflow and selected results. It is not a claim of clinical prediction or diagnostic performance.*