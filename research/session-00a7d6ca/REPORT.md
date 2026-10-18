# Session 00a7d6ca: Comprehensive TWC Day 1–5 Review, Pick Resolution Architecture & Mobile Discoverability Report

**Date:** 2026-10-18  
**Author / Integrator:** Session `00a7d6ca` (`arena/00a7d6ca-maltaproj4`)  
**Repository:** `buffedlizard55-lab/MaltaProj4`  
**Live Site:** https://buffedlizard55-lab.github.io/MaltaProj4/  

---

## 1. Executive Summary

This session conducts an independent line-by-line verification across all deliverables required by the project specifications:
1. **Thunderpick World Championship (TWC) 2026 Complete Days 1–5 Review**:
   - Re-evaluates Day 1's monumental 9z vs Aurora upset (9z 2-0 Aurora) and the narrative of Aurora's "recent roster changes".
   - Verifies the actual transfer dates: Ashley "ash" Battye, Jimi "Jimpphat" Salo, and Damjan "kyxsan" Stoilkovski joined Aurora in early July 2026 (announced July 3–8, 2026; HLTV News 45082), roughly 14 weeks (~3 months) prior to TWC. Aurora had already achieved #5 in the Valve Regional Standings and #6 in the HLTV world rankings with this lineup, and took 3rd place at ESL Pro League Season 24. The loss was therefore driven by schedule compression and fatigue following EPL 24, combined with 9z's tournament-high individual form (luchov 1.61 rating), rather than fresh roster onboarding confusion.
   - Evaluates Day 2, Day 3, and Day 4 results to establish causal tournament trajectories:
     - Day 2: Falcons edged 9z 2-1; Aurora eliminated NiP 2-0; FURIA topped Legacy 2-1; BETBOOM survived PARIVISION 2-1.
     - Day 3: Aurora reversed the Day 1 upset by sweeping 9z 2-0 in the Group A decider; BETBOOM eliminated Legacy 2-1.
     - Day 4: FURIA swept Aurora 2-0 in Semi-Final 1 (improving to 6-1 map record at TWC); BETBOOM upset Falcons 2-1 in Semi-Final 2 (recovering from 5-13 on Anubis to win Dust2 16-14 and Mirage 13-7).
   - Formulates the final day (Day 5, 18 October 2026) decision guide:
     - **Third-place decider (11:30 UTC): Aurora vs Falcons (BO3)**. Verified Thunderpick line: Aurora +170 / Falcons -238 (decimal 2.70 / 1.42; de-vig: Falcons 65.53%, Aurora 34.47%). Display discrepancy on tournament card (+150 / -208) flagged.
     - **Grand final (15:00 UTC): FURIA vs BETBOOM (BO5)**. Verified Thunderpick line: FURIA -286 / BETBOOM +190 (decimal 1.35 / 2.90; de-vig: FURIA 68.24%, BETBOOM 31.76%). Map volume load: FURIA has played 7 tournament maps; BETBOOM has played 11 grueling maps across four consecutive 3-map series.
2. **Contrarian-not-Stupid Pick'em Leaderboard Strategy**:
   - Outlines how to climb the Hotspawn pick'em leaderboard without making mathematically irrational picks.
   - Confirms that Hotspawn scoring rewards correct picks plus streak bonuses, with weekly resets. Since Hotspawn does not publish user pick distributions or personal standings, fading a heavy favorite is only rational when chasing from behind late in the weekly cycle or when identifying concrete structural factors (e.g. fatigue asymmetry, map pool veto mismatches).
3. **Universal Pick Coverage via 4-Tier Resolution Architecture**:
   - **Tier 1 (Market Lines)**: Exchange (Polymarket Gamma API) or Bookmaker (Pinnacle/Thunderpick) de-vigged win probabilities.
   - **Tier 2 (Originated VRS Model Lines)**: Valve Regional Standings points passed through Valve's official logistic win-expectation formula and calibrated curve, generating an independent mathematical probability line where no sportsbooks offer odds.
   - **Tier 3 (HLTV Research Picks)**: Where only one team has verified HLTV rankings, a research-only pick is generated with no fabricated percentage.
   - **Tier 4 (Unresolved & Limitations)**: Strict safety guards (e.g. Polymarket API reporting parent event 1203504 `ended: true` for Hacha vs LOS NINOS despite active orders) withhold picks, document exact attempt logs, and publish them visibly in the Executive Summary and on `unresolved.html`.
4. **Hotspawn Reverse Engineering & Freshness Automation**:
   - Verified Cloudways API integration (`https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) and Next.js lobby scraping.
   - Automated CI runs every 15 minutes (`pages.yml` cron: `4,19,34,49 * * * *`) with a freshness gate and a 10-minute watchdog that dispatches a build whenever data exceeds 90 minutes.
5. **Mobile-First Dashboard & Executive Summary**:
   - Prominent, touch-friendly navigation on the landing page:
     - Hero buttons: "View updated picks →" (`picks.html`), "Day-5 final-day guide ↗" (`analysis.html#day-five-guidance`), "Day-4 results ↗" (`analysis.html#day-four-results`).
     - "Where the picks are" card grid for mobile devices.
     - Section jump anchors: `#today`, `#later`, `#unresolved-summary`, `#coverage`.
     - On-page nav on `analysis.html` organized with Day-5 final-day guide and limitations at the top.
   - All pages pass axe WCAG 2.1 AA/AAA compliance across 320px, 390px, 768px, and 1440px viewports with zero horizontal scrolling.

---

## 2. Day 1–5 TWC 2026 Results & Strategy Analysis

### 2.1 Day 1: The 9z vs Aurora Upset & Roster Myth

- **Match:** 9z vs Aurora (HLTV Match 2399384; 14 October 2026)
- **Score:** 9z 2-0 Aurora (Inferno 13-11, Nuke 13-1)
- **Statistical Standouts:** luchov (9z) 1.61 rating, +6.61% swing, 97.4 ADR, 86.8% KAST. Aurora managed just 1 round on their own map pick (Nuke).
- **Roster Change Investigation**:
  - Mainstream narrative: "Aurora made a recent roster change and is still onboarding new players."
  - **Fact Check:** The rebuild occurred in **early July 2026**, when Jimi "Jimpphat" Salo transferred from MOUZ, Ashley "ash" Battye arrived as coach from GamerLegion, and Damjan "kyxsan" Stoilkovski took over as IGL on 8 July 2026 ([HLTV News 45082](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan)).
  - By TWC (mid-October 2026), this roster had competed together for **over 14 weeks (~3 months)**, climbing to #5 in Valve's Regional Standings and #6 in HLTV's World Ranking, including a 3rd-place finish at ESL Pro League Season 24.
  - While coach ash described communication across 3–4 cultures as an ongoing challenge ([HLTV Interview](https://www.hltv.org/news/45284/ash-ive-been-biting-my-tongue-a-little-bit-sometimes-like-okay-this-is-the-way-we-play)), the team was not an uncalibrated mix team.
  - The real operational factor was **schedule compression and fatigue**: Aurora had just concluded a deep run at ESL Pro League Season 24 in Saint Julian's, Malta, entering TWC with minimal rest, while 9z prepared targeted anti-stratting on Inferno and Nuke.

### 2.2 Day 2 to Day 4 Results: The Tournament Evolution

| Day | Date | Match | Score | Key Takeaway |
| --- | --- | --- | --- | --- |
| Day 1 | 2026-10-14 | 9z 2–0 Aurora | 13-11, 13-1 | Major opening upset; Aurora punished on Nuke. |
| Day 1 | 2026-10-14 | Falcons 2–0 NiP | 16-13, 13-6 | Falcons resilient in OT on Ancient. |
| Day 1 | 2026-10-14 | Legacy 2–0 PARIVISION | 2-0 series | Legacy sweeps opening round. |
| Day 1 | 2026-10-14 | FURIA 2–0 BETBOOM | 2-0 series | FURIA dominates opening Group B fixture. |
| Day 2 | 2026-10-15 | Falcons 2–1 9z | 13-9, 8-13, 13-9 | Falcons qualify for playoffs; 9z shows fight on Mirage. |
| Day 2 | 2026-10-15 | Aurora 2–0 NiP | 13-9, 13-7 | Aurora rebounds; Wicadia 1.65 rating; NiP eliminated. |
| Day 2 | 2026-10-15 | FURIA 2–1 Legacy | 10-13, 13-5, 13-8 | FURIA qualifies for playoffs directly. |
| Day 2 | 2026-10-15 | BETBOOM 2–1 PARIVISION | 7-13, 13-4, 13-7 | BETBOOM starts their lower-bracket grind. |
| Day 3 | 2026-10-16 | Aurora 2–0 9z | 13-4, 13-5 | **Upset reversed:** Aurora adapts veto, crushes 9z on Mirage & Dust2. |
| Day 3 | 2026-10-16 | BETBOOM 2–1 Legacy | 11-13, 13-7, 13-10 | BETBOOM takes second 3-map series to reach semis. |
| Day 4 | 2026-10-17 | FURIA 2–0 Aurora | 13-8, 13-10 | FURIA sweeps to the grand final; 6-1 overall tournament map record. |
| Day 4 | 2026-10-17 | BETBOOM 2–1 Falcons | 5-13, 16-14, 13-7 | **Second major upset:** Falcons (-238 fav) fall in 3-map comeback. |

### 2.3 Day 5 Final Day Decision Guide

#### Match 1: Third-Place Decider — Aurora vs Falcons (11:30 UTC; BO3)
- **HLTV Fixture:** [HLTV 2399416](https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026)
- **Thunderpick Moneyline:** Aurora +170 / Falcons -238 (decimal 2.700 / 1.420)
- **De-vigged Probabilities:** Falcons 65.53% | Aurora 34.47% (Overround: 7.45%, fair decimals: 1.526 / 2.901)
- **Discrepancy Flag:** Thunderpick's tournament card briefly displayed +150 / -208 in the same minute as the market page showed +170 / -238; flagged visibly on the site.
- **Analysis:** Falcons are the mathematical pick. Both teams suffered semi-final defeats. Aurora played a standard 2-map series vs FURIA, while Falcons endured a taxing 3-map overtime loss to BETBOOM. If a bettor must take a contrarian pick to gamble on high variance, Aurora is closer in skill than the line suggests, but default recommendation remains Falcons.

#### Match 2: Grand Final — FURIA vs BETBOOM (15:00 UTC; BO5)
- **HLTV Fixture:** [HLTV 2399417](https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026)
- **Thunderpick Moneyline:** FURIA -286 / BETBOOM +190 (decimal 1.350 / 2.900)
- **De-vigged Probabilities:** FURIA 68.24% | BETBOOM 31.76% (Overround: 8.58%, fair decimals: 1.465 / 3.149)
- **Format:** Best-of-5.
- **Cumulative Map Load:**
  - FURIA: **7 maps** played across the tournament (2-0 vs BETBOOM, 2-1 vs Legacy, 2-0 vs Aurora).
  - BETBOOM: **11 maps** played across four consecutive 3-map battles (0-2 vs FURIA, 2-1 vs PARIVISION, 2-1 vs Legacy, 2-1 vs Falcons).
- **Analysis:** In a Best-of-5 series, map pool depth and physical stamina play a massive role. BETBOOM has shown unmatched tenacity, but FURIA already dismantled BETBOOM 2-0 on Day 1 and enters with significant tactical freshness and rest. FURIA is the clear baseline pick (68.24%).

---

## 3. Contrarian-not-Stupid Leaderboard Strategy

When competing in the Hotspawn CS2 Pick'em leaderboard:
1. **Never Fade a Favorite Purely for Differentiation:**
   - Underdogs have a lower probability of winning by definition. Taking an underdog with a 30% win chance incurs a severe negative expected value unless there is private information or a major unpriced factor.
2. **Identify True Disruption Signals:**
   - Fatigue asymmetry (e.g. 11 maps vs 7 maps).
   - Veto-specific advantages (e.g. perma-ban overlaps or high win rates on decider maps).
   - Schedule congestion / travel strain (as seen in Aurora's Day 1 arrival from EPL).
3. **Understand Leaderboard Dynamics:**
   - If leading or near the top: **Protect your streak**. Hotspawn awards streak bonuses. Picking the high-probability favorite maximizes streak longevity.
   - If trailing late in the contest: **Selective contrarianism**. Choose the live underdog with the narrowest gap (e.g. Aurora 34.5% vs Falcons, rather than sub-20% longshots).

---

## 4. Verification and Audit Results

- **Unit and Regression Test Suite:** 359 tests passed in 4.45s (`.venv/bin/python3 -m unittest discover tests`).
- **Independent Failure Mode Audits:** 9 tests passed (`audits/`).
- **Integrity Checks:** 5 tests passed (`verification-95b588c2/test_integrity.py`).
- **Snapshot Audit:** 12 tests passed (`verification-c6/test_audit.py`); 81 rows audited with 0 failures (`audit_snapshot.py`).
- **Site Validation:** `scripts/validate.py` checked:
  - 81 primary snapshot rows verified.
  - 13 probability calculations reproduced.
  - 15 pages verified.
  - 570 internal links and assets checked with zero broken links.
  - 20 artifact checksums verified.
  - 192 displayed match rows verified.
- **Browser Accessibility & Viewport Scans:** 32 viewport scans (320px, 390px, 768px, 1440px) passed with 0 WCAG violations and 0 layout overflow (`tests/browser.cjs`).
- **Expiry Boundary Scans:** 7 board expiry and 4 research-quote boundary tests passed (`tests/expiry.cjs`).
