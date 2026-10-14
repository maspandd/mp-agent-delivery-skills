---
name: estimate-delivery-plan
description: "Turn a project estimate (modules, phases, discovery/development/migration/UAT sprints) into a delivery-plan Google Sheet: estimate review, team scenarios, pros and cons, module stage timeline and dated calendar with holidays. Use whenever the user asks to compare 1 team vs 2 teams, plan sprints from an estimate, build a timeline or gantt, or date a plan from a start month, even if they only paste or link an estimation sheet."
license: Proprietary. Internal use only.
compatibility: Needs read and write access to Google Sheets, through the Claude Google Sheets connector or any Google Sheets MCP server or API client.
metadata:
  author: Pandu
  version: "1.0.0"
---

# Estimate to delivery plan

This skill turns a sprint estimate into a delivery plan that an engineering manager can defend to a client. The output is a Google Sheet where every number is a formula, so the plan updates when an estimate or a setting changes.

If a `google-workspace` skill is installed, read it and its `references/sheets.md` before the first Sheets call. This skill adds the planning rules and the workbook layout on top of it.

If that skill is not installed, use the Google Sheets tool that this agent has. Tool names below, such as `get_values` and `update_spreadsheet`, come from the Claude connector. Map each one to the equivalent call in your tool. If the agent has no Google Sheets tool, stop and tell the user. Do not write the plan to another format unless the user asks.

## The user's planning rules

These rules came from the user. Apply them unless the user changes them for a project.

- **Whole numbers only.** Estimates, sprint counts and durations are integers. Use number format `0`. Never write 0.5 or 1.5.
- **Sprints start at 1.** Start and end are sprint numbers, inclusive. A stage from 1 to 4 runs in sprints 1, 2, 3 and 4. Never show sprint 0 as a number.
- **Stage order per module:**
  1. **Sprint 0 (discovery):** gather requirements, tech discussion, planning. If discovery is 1 sprint, all three share it. If discovery is 2 sprints or more, gathering requirements takes the first sprints, and tech discussion and planning share the last one. "Sprint 0" is a stage label, not a sprint number.
  2. **Development.** Testing / SIT runs inside every development sprint. It never gets its own sprint.
  3. **UAT.** Dedicated sprints per phase. All modules of the phase share one UAT window. Typical windows from past estimates: 3, 3, 2, 1.
  4. **Release.** Deploy to production and production test share one sprint per phase by default. Make this an input cell, because the user may change it.
  5. **Data migration.** Dedicated sprints after the release sprint, module by module.
- **One Tech Lead leads all squads.** Count the Tech Lead once, never once per squad.
- **Squads wait while client staff run UAT** by default. Make this a Yes/No input so the user can test overlap.
- **Person-sprints** = people x sprints on the project. Count each squad from its first sprint to the end of its last phase, including migration.

Team composition changes per project. Past examples: a 4-person team (1 Tech Lead, 1 back-end, 2 front-end), and squads of 7 (PM, BA, 3 to 4 engineers, QA, UI/UX) with an optional Chief Architect. Put headcount in input cells and confirm it before building.

## Workflow

### 1. Read the estimate

Find, for each module: phase, discovery, development and migration sprints, dependencies and main risks. Find UAT sprints per phase. Check that the totals are formulas and that they add up. Note any figure the estimate does not contain, such as release time.

### 2. Review the estimate before building

Report problems in chat first, because they change the schedule. Check for:

- **Dependency gaps.** A module that every other module needs (often login and access control) scheduled last in its phase. A module marked "no dependency" that clearly needs member or organization data.
- **Scope overlap.** The same feature listed under two modules. It double-counts effort, and it becomes an ownership conflict if two squads build those modules.
- **Sequential waste.** Team idle during discovery, migration or UAT because the estimate assumes strict sequence.
- **Bottleneck roles.** One back-end engineer carrying both development and all migration scripts.
- **Team mismatch.** Estimates made for one team shape but planned for another.
- **Document claims that do not match the arithmetic.** For example a "saves 45%" claim when the numbers give 36% to 43%. Show the calculation.

### 3. Confirm what changes the plan

Ask one question only when a wrong guess is costly. Otherwise state the assumption and proceed. The usual open items:

- Team composition per squad, and which strategies to compare.
- Phase 1 build and migration time when two squads share it. Derive a default from module dependencies, for example Squad A builds Organization then Members while Squad B builds User & Access, and mark it as an assumption.
- Start date, sprint length and holidays, for the calendar.
- Audience. An internal sheet can use TL, BE, FE and UAT. A client or stakeholder sheet uses plain terms (see below).

### 4. Build the workbook

Create a new spreadsheet or add tabs, as the user asks. Use these tabs. Leave out a tab the user does not need.

| Tab | Contents |
|---|---|
| Summary | One row per strategy: people, finish sprint, months, time saved, person-sprints, best fit. A phase table with the sprint each phase finishes. A difference row. |
| Pros and Cons | Option, Pro or Con, Point. Pros in green, cons in red, option name merged down. Any point with a number is a formula that pulls from Summary or Timeline. |
| Timeline | Phase table (discovery, development, migration, build, UAT, total including release). Settings in yellow cells. One phase schedule per strategy: build start and end, UAT start and end, phase finished. |
| Module Timeline | Module estimates as yellow inputs (phase totals on Timeline are SUMIFS over these). One gantt per strategy: module x nine stage rows, start, end, sprints, and a coloured bar across sprint columns. A check cell that confirms the finish sprints match Summary. |
| Calendar | Dated version of both strategies (see below). |
| Team | Roles, people per squad, what each role does. Headcount table per strategy. |
| Tech Stack, Delivery Rules | Only when the user supplies a strategy document with these sections. |
| Glossary | For stakeholder versions: sprint, phase, squad, UAT, SIT, release, data migration, person-sprint, and any regulation named. |

### 5. Verify

Read back every computed range with `get_values`. Check: no error values, totals match the source estimate, the Module Timeline check cell says it matches Summary, and every Pros and Cons formula renders text. Fix before replying.

### 6. Reply

Lead with a results table (finish sprint, months, person-sprints per strategy). Then the assumptions to confirm, then the risks found, such as a go-live inside the year-end break. Link the file. Do not recap the build steps.

## Scheduling logic

Use these formulas so the plan stays live.

- **Module stages:** Sprint 0 starts at the module start. Development starts at start + discovery. SIT start = development start, SIT end = development end. UAT for the phase starts the sprint after the last module of the phase finishes development. Release starts after UAT and lasts the release input. The first module's migration starts after release. Each later module's migration starts after the previous module's migration.
- **Next module on the same squad** starts the sprint after the previous module's development ends, not after its migration, unless a dependency forces later.
- **Dependencies:** start = MAX(end of previous module on the same squad, end of each dependency's development) + 1.
- **Next phase:** if squads wait for UAT, start after the previous phase is finished. Otherwise start after its build ends.
- **Strategy 2 (two squads, shared first phase):** both squads build Phase 1, then split into streams, for example Finance and Operations. Assign each later module to a squad. Each stream finishes on its own date. The project finishes at the later one.
- **Hybrid (second squad joins later):** the second squad's first sprint is an input cell.

## Calendar tab

- **Start date:** a yellow input. Default to the first working day of the week the user names, and say which date you picked.
- **Sprint dates:** working days per sprint = weeks per sprint x 5. Sprint 1 start = WORKDAY(start - 1, 1, holidays). End = WORKDAY(start, days - 1, holidays). Next start = WORKDAY(previous end, 1, holidays). Build 70 sprint rows.
- **Holidays:** list each year's year-end break (weekdays from 24 December to 1 January). Mark Christmas Day and New Year's Day as public holidays and the rest as year-end break. Leave yellow rows for more dates. Say in a note that Chinese New Year, Hari Raya and Deepavali (Singapore) and Lebaran (Indonesia) are not included unless the user adds them.
- **Named ranges:** SprintStart, SprintEnd, SprintBreakDays, YearEndBreak. They keep formulas short.
- **Key dates per strategy:** project start, each phase live (end of its release sprint), project finished (last migration), duration in months, working days lost to the break, and go-live sprints that fall in a break.
- **Month gantt:** one column per month, coloured with conditional formatting when any part of a stage falls in that month. A red row marks months that contain break days.
- **Flag in the reply** any release sprint that crosses the year-end break, because client staff are on leave.

## Stakeholder-friendly version

When the user asks for a client or stakeholder version, make a separate spreadsheet with no links to the internal file.

| Internal term | Stakeholder term |
|---|---|
| UAT | Testing by [client] staff |
| SIT | Testing / SIT (explained in the glossary) |
| Migration | Data move, or data migration |
| TL | Technical lead |
| BE / FE | Back-end developer / front-end developer |
| Person-sprints | Total effort (person-sprints), defined in the glossary |

Keep the same numbers and formulas. Write the module names the client uses. Add the Glossary tab.

## Google Sheets mechanics that broke before

- **Locale.** A new sheet created from an Indonesian account gets locale `in_ID`, and English formulas then show errors. Set `locale` to `en_US` and the client's time zone (for example `Asia/Singapore`) with `updateSpreadsheetProperties` before writing formulas.
- **Write quota.** Sheets allows about 60 writes per minute. On a quota error, wait 60 seconds and retry the same call. Put all formatting for a tab in one `update_spreadsheet` batch.
- **Payload size.** A formula grid over about 30 KB can fail. Use named ranges to shorten formulas. Write the first one or two rows of a repeated block, then fill the rest with `copyPaste` and `PASTE_FORMULA`.
- **Inserted rows shift references.** After `insert_dimension`, re-read before writing below the insert, and check that formulas elsewhere point at the right rows.
- **Conditional formatting.** When stage names change, update the existing rules by index rather than adding duplicates.
- **Inputs and sources.** Inputs get a yellow fill and blue text. Put the source of each input in a cell note, for example the estimate file and tab, or "assumption, confirm with team".
- **No conversation in the workbook.** Do not write "updated per feedback" or name tabs "v2". Describe changes in the reply.

## Writing in the sheet

Use short, plain sentences in active voice. State a fact with a number rather than an adjective, for example "Costs 566 person-sprints against 480, about 18% more" rather than "significantly more expensive". When the user writes a pro or con in Indonesian, add it in the sheet's language and keep its meaning.