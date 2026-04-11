# ICE QA Engineer Onboarding Checklist

## Before Your First Day

Your manager and HR will send you a welcome email 3–5 days before your start date with:
- Building access instructions and parking details
- Arrival time and meeting point (Security desk, Lobby Level, Building A)
- Dress code reminder: business casual for your first day
- Pre-reading: ICE company overview (public investor relations page)
- Emergency contact form (bring completed on Day 1)

## Day 1 — Welcome & Setup

### Hour-by-Hour Schedule
- **8:30 AM** — Arrive at Building A lobby. Security will have your temporary badge ready.
- **8:45 AM** — IT Support (Room 2-104): Collect your MacBook Pro 16", two monitors, keyboard, mouse, and headset
- **9:15 AM** — Your manager meets you at your desk for a welcome chat and team overview
- **10:00 AM – 12:00 PM** — HR Orientation Session (Conference Room "Hudson"):
  - Company overview and organizational structure
  - Benefits enrollment walkthrough (you have 30 days to complete this)
  - Sign Non-Disclosure Agreement (NDA) and Acceptable Use Policy
  - Complete I-9 employment verification (bring valid ID + work authorization)
  - Set up Workday profile (personal info, emergency contacts, direct deposit)
- **12:00 PM – 1:00 PM** — Team lunch (your manager will arrange this)
- **1:00 PM – 2:00 PM** — IT setup time at your desk:
  - Activate corporate email and set up Outlook
  - Install Slack and join initial channels (#ice-general, #qa-team)
  - Set up two-factor authentication (Duo Mobile)
- **2:00 PM – 3:00 PM** — Facilities tour with your onboarding buddy:
  - Cafeteria, coffee bar, break rooms, restrooms
  - Conference rooms, quiet rooms, focus pods
  - IT Help Desk, HR office, Security desk
  - Parking garage and badge access points
- **3:00 PM – 5:00 PM** — Free time to set up your workstation and explore Workday

### Day 1 Checklist
- [ ] Pick up employee badge from Security desk (Lobby Level, Building A)
- [ ] Collect laptop and peripherals from IT Support (Room 2-104)
- [ ] Attend HR orientation session
- [ ] Sign NDA and Acceptable Use Policy
- [ ] Complete I-9 employment verification with HR
- [ ] Set up Workday profile (personal info, emergency contacts, direct deposit)
- [ ] Activate corporate email and set up Outlook
- [ ] Set up Duo Mobile for two-factor authentication

## Day 2 — IT Access & Tools

- [ ] Submit IT access requests via ServiceNow for:
  - Jira (project: ICE-QA)
  - Confluence (QA team space)
  - GitHub Enterprise (org: ice-engineering)
  - VPN (Cisco AnyConnect)
  - Slack (join channels: #qa-team, #qa-automation, #qa-regression-results, #qa-environments, #ice-general)
- [ ] Install development tools: VS Code, Python 3.11+, Node.js 18+, Playwright, Git
- [ ] Configure VPN and verify connectivity to DEV environment
- [ ] Complete CyberArk onboarding for privileged access management
- [ ] Verify email is working (send a test email to your manager)
- [ ] Explore internal Confluence wiki — bookmark the QA team space

## Day 3 — Team Introduction

- [ ] Meet your QA Lead, Sarah Chen, for a team walkthrough and role expectations discussion
- [ ] Shadow the 9:30 AM sprint standup (just observe — no need to present)
- [ ] Review the QA team wiki on Confluence (bookmark key pages)
- [ ] Get added to the QA sprint board in Jira
- [ ] Pair with your onboarding buddy for a codebase tour (test automation repo)
- [ ] Meet the other QA sub-teams (Manual QA, Performance QA) informally

## Days 4–5 — Environment & Tools Deep Dive

- [ ] Clone the test automation repository from GitHub
- [ ] Follow the README to set up your local development environment
- [ ] Run the existing Playwright regression suite locally (ask your buddy if anything fails)
- [ ] Study the Page Object Model (POM) structure used in the automation framework
- [ ] Read the ICE QA Automation Standards document on Confluence
- [ ] Set up your Jira dashboard and filters

## Week 1 — Compliance & Training

- [ ] Complete mandatory compliance training modules in Workday Learning:
  - Material Non-Public Information (MNPI) Awareness (~30 min)
  - Insider Trading Prevention (~20 min)
  - Data Handling and Classification (~20 min)
  - Information Security Fundamentals (~30 min)
  - Anti-Money Laundering (AML) Basics (~20 min)
- [ ] Read and acknowledge the ICE Code of Conduct
- [ ] Complete cybersecurity awareness training (~45 min)
- [ ] Complete your health insurance enrollment in Workday (deadline: 30 days from start date)

## Week 2 — Hands-On Learning

- [ ] Attend first paired testing session with your assigned buddy
- [ ] Review existing test plan templates in Confluence
- [ ] Run the regression suite locally and analyze a few test cases in detail
- [ ] Write your first practice test case (with guidance from your buddy)
- [ ] Attend QA Sync (cross-team meeting, Wednesday 11:00 AM)
- [ ] Start reviewing open PRs in the test automation repo to understand the code review process

## Week 3 — First Solo Assignment

- [ ] Receive your first solo test case assignment from the QA Lead
- [ ] Write and execute the test case independently
- [ ] Submit your test case for code review via GitHub PR
- [ ] Incorporate code review feedback and get your PR merged
- [ ] Attend your first sprint retrospective
- [ ] Schedule a 30-day check-in with your manager

## 30-Day Milestone

- [ ] Complete 30-day check-in with your manager
- [ ] Ensure all compliance training is **100% complete** in Workday
- [ ] Health insurance enrollment confirmed (hard deadline)
- [ ] Have at least **2 merged PRs** in the test automation repo
- [ ] Be actively participating in daily standups with updates
- [ ] Know how to file a bug report in Jira using the team template

## 60-Day Milestone

- [ ] Be independently writing and submitting test cases without pairing
- [ ] Have at least **5 merged PRs** with clean code review history
- [ ] Be reviewing other team members' PRs (at least 2 reviews per sprint)
- [ ] Understand all 4 test environments (DEV, QA, STAGING, PROD) and when each is used
- [ ] Have run at least one API test using the pytest/requests framework
- [ ] Complete 60-day check-in with your manager

## 90-Day Milestone — End of Probation

- [ ] Complete 90-day performance review with your manager (this marks the end of your probationary period)
- [ ] Be a fully contributing member of the sprint team
- [ ] Have at least **10+ merged PRs** across UI and API test automation
- [ ] Be comfortable with the full CI/CD pipeline and how tests integrate
- [ ] Be comfortable with the QA sign-off process for releases
- [ ] 401(k) company match becomes active (automatic enrollment through Fidelity)
- [ ] Consider setting up tuition reimbursement if pursuing relevant coursework

## Common First-Week Questions

**Q: When will I get my first paycheck?**
A: ICE pays bi-weekly on Fridays. Your first paycheck will be on the first pay date that falls at least 2 weeks after your start date. Set up direct deposit in Workday on Day 1 to avoid paper check delays.

**Q: What if I need to leave early or come in late?**
A: Just let your manager know via Slack. During your first week, flexibility is understood — you're still getting set up.

**Q: Who do I ask if I'm stuck on something?**
A: Your onboarding buddy is your first point of contact. For IT issues, go to the Help Desk (Room 2-104, ext. 2-HELP). For HR questions, contact Jessica Martinez (Room 3-210).

**Q: How long until I get access to all the tools?**
A: Most ServiceNow requests are processed within 24–48 hours. VPN and GitHub usually take 24 hours. CyberArk access may take up to 3 business days due to security review.

**Q: Can I install my own software on the laptop?**
A: Personal software that doesn't require admin privileges is generally fine (music apps, personal browser profiles). Development tools or anything requiring admin installation must go through an IT approval request on ServiceNow.
