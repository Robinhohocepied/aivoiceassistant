# AI Voice Receptionist – MVP Product Requirements Document (Final)

## 1. Overview

| Category | Detail |
| :--- | :--- |
| **Industry** | Healthcare – Medical and Dental Practices |
| **Product Name** | AI Voice Receptionist |
| **Target Market** | Liège, Belgium (Pilot Phase) |

---

## 2. Problem Statement & Solution

### Problem Statement
Medical and dental clinics in Belgium (Liège) lose revenue due to **missed calls** and are constrained by **manual scheduling**. Human staff are costly and unavailable outside office hours, leading to patient frustration and lost appointment opportunities.

### Solution Summary
An **AI-powered voice receptionist** that automatically handles patient phone calls, collects necessary details, schedules appointments, sends confirmations, and routes urgent issues.  
Designed for ease of setup with minimal coding, optimized for Belgian clinics.

---

## 3. Core Features

1. **24/7 French-language AI call handling** (natural, human-like voice).
2. Collects patient name, visit reason, and preferred time.
3. **Books via Google Calendar** or compatible scheduling API.
4. Sends automatic confirmations/reminders (Email/SMS).
5. Handles rescheduling and emergency routing.
6. **Fallback to human receptionist** if AI gets stuck or for urgent calls.
7. Clinic staff dashboard for rule updates and metrics.
8. Simple setup and onboarding.

---

## 4. Technical Components (MVP Stack)

| Component | Purpose | Estimated Cost |
| :--- | :--- | :--- |
| **AI Voice Handling** | Core conversational AI/voice service | vapi.ai (€99/month) |
| **Automation/Integration** | Connecting AI output to scheduling system | n8n (€25/month) |
| **Scheduling** | Appointment management system | Google Calendar API (or equivalent) |
| **Messaging** | Sending confirmations/reminders | Email/SMS provider |
| **Manual Override** | Backup for third-party platform failure | Human intervention protocol |

---

## 5. Ideal Customer Profile (ICP) – Refined

- **Geography:** Small or independent healthcare practices (dentists, GPs, physiotherapists, dermatologists) in **Liège, Belgium**.  
- **Current Practice:** Reliance on phone-based scheduling and manual calendars (Google Calendar or paper).  
- **Goal:** Automate booking, reduce missed calls, and provide 24/7 service **without complex setup**.

---

## 6. Critical Risks and Mitigation

| Risk Area | Concern/Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **AI Voice Quality and Conversational Flow** | If the French voice sounds robotic or confusing, patient satisfaction drops. | **Action:** Script and test dialogues with native speakers; use top-tier text-to-speech for natural tone and pacing. |
| **Core Integration Failure (Scheduling)** | Booking errors via the Google Calendar API could block adoption. | **Action:** Prioritize integration testing; define human fallback to collect data and inform staff immediately. |

---

## 7. Business Model & Pricing (Revised)

### Tiered Pricing for Small Clinics (Launch Phase)

| Package | Setup Fee | Monthly Fee | Description |
| :--- | :--- | :--- | :--- |
| **Pilot Offer** | **€0 (Free)** | **€0 (1 Month)** | Limited hours / 1 phone line for trial. Converts to paid plan after successful trial. |
| **Starter** | **€750** | **€400/month** | 1 phone line, up to 300 calls/month, basic scheduling + email/SMS confirmation |
| **Pro** | €2,000 | €700/month | 2 lines, up to 600 calls/month, rescheduling + emergency routing |
| **Clinic+** | €3,000 | €1,000/month | Custom integrations, dashboard automation, priority support |

**Rationale:**  
The lowered Starter setup fee (€750) reduces financial friction for small clinics, supporting faster adoption while preserving margins (45–70%).

---

## 8. Value Proposition

- Clinics save **€33K–€47K/year** versus hiring human receptionists.  
- **Zero missed calls** and 24/7 patient accessibility.  
- Simple setup and local French-language support.  
- Fast ROI, typically **within 2 months**.

---

## 9. Go-To-Market Strategy

1. **Market Entry (Liège Pilot Stage):** Target 5–10 small clinics. Offer the **Pilot Plan** to collect data and testimonials.  
2. **Messaging:** “Your 24/7 AI receptionist – **for less than €2/hour.**”  
3. **Sales Approach:** Direct outreach (LinkedIn, associations), healthcare events (Liège MedTech), referral incentive (one free month).  
4. **Marketing Channels:**  
   - French-language landing page.  
   - Targeted ads (“standardiste médical Liège”).  
   - Short demo videos showing live AI calls and scheduling.

---

## 10. Impact Measurement Plan

| Objective | Metric | Target |
| :--- | :--- | :--- |
| **Reduction in Missed Calls** | `Missed Call Rate = Missed Calls / Total Incoming Calls` | ≥ **80–90%** reduction within 1 month |
| **Time Saved for Staff** | AI call minutes handled vs. baseline manual time | **3+ hours/day** saved |
| **Patient Satisfaction** | 1-question SMS survey (1=Non, 5=Très satisfait) | **+25–30%** improvement in score |

**Reporting:**  
Each clinic receives a visual performance dashboard (e.g., Google Data Studio or internal tool) showing:  
- Calls answered by AI  
- Appointments booked  
- Missed-call trend  
- Estimated hours saved  
- ROI estimation

---

## 11. Summary

The AI Voice Receptionist delivers **immediate, measurable ROI** for small Belgian clinics by cutting missed calls, reducing admin time, and improving patient satisfaction.  
The pilot-first, low-barrier pricing model enables early traction and case-study generation while maintaining sustainable margins.

---

12. Strategy & Roadmap (Added Section)

The AI Receptionist will begin as a local automation tool for Liège clinics, then scale regionally (Wallonia → Brussels → Luxembourg).
We’ll remain lean and self-funded, requiring only ~15 hours/week combined from founders.

Growth Stages:

Founding Partner Pilot (0–3 months): 5 clinics, free 3-month pilot → 50% discount for 12 months.

Validation Stage (4–12 months): Paid rollout (€450/month) with free trial; goal €5k MRR.

Scaling Stage (Years 2–3): Expand to 70+ clinics; target €38–40k MRR.

Roles:

Robin: Product, sales, onboarding.

Reet: Backend, automation (n8n, VAPI, APIs).

Shared: UX, design, content.

13. Financial Summary (Added Section)

Revenue Assumptions:

ARPU: €450 → €550 (3 years).

Cost: ~€200/month.

Profit margin: ≈90%.

Profit split: 50/50 (Robin & Reet).

Year	Avg Clinics	ARPU (€)	Revenue (€)	Profit (€)	Each Founder (€)
1	10	450	54,000	52,000	26,000
2	35	500	210,000	202,000	101,000
3	70	550	462,000	444,000	222,000

Goal: €38–40k MRR by Year 3, providing ~€15k net/month each.

14. Key Milestones

Month 3: 1 live pilot clinic & testimonials.

Month 6: 5+ clinics, €2–3k MRR.

Month 12: 10 clinics, €5k MRR.

Year 2: 35 clinics, €17k MRR.

Year 3: 70 clinics, €38k+ MRR.

15. Exit & Expansion Paths

Once stable and profitable:

Expand regionally across Benelux.

Convert to SaaS (self-service setup).

License AI backend to local scheduling providers (Doctena, Progenda, etc.).

