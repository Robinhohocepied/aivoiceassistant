# AI‑Powered Appointment Booking Assistant – Functional Requirements (FRD)

## 1. Introduction
This document outlines the functional requirements for an AI‑powered appointment booking assistant prototype. The assistant interacts with patients via WhatsApp, gathers booking details in French, and schedules appointments in a shared calendar for both the patient and the clinic. The system is designed to reduce missed calls and improve scheduling efficiency for small medical and dental practices.

## 2. Purpose
The purpose of this document is to define the functional requirements of the AI appointment booking assistant. It serves as a blueprint for developers and stakeholders, ensuring that the system meets the needs of both patients and clinic staff.

## 3. Scope
This document covers the functional requirements for the prototype of the AI appointment booking assistant, including messaging, conversation flow, scheduling, notifications, and error handling. Non‑functional requirements such as performance and security are also addressed.

## 4. Stakeholders
- **Patients** who book appointments via WhatsApp.
- **Clinic staff** who manage scheduling and patient data.
- **Developers and technical teams** responsible for building and maintaining the system.
- **Compliance officers** ensuring GDPR and data privacy requirements are met.

## 5. Functional Requirements

### 5.1 Messaging
- The system shall receive incoming messages from patients via **WhatsApp Business API**.
- The system shall send outgoing messages to patients via WhatsApp, including confirmations and reminders.
- The system shall handle initial greeting messages and closure messages **in French**.

### 5.2 Conversation Flow
- The system shall greet the patient and collect their **name**, **reason for visit**, and **preferred time**.
- The system shall interpret **free‑form text** responses and extract relevant details.
- If any required field (name, reason, preferred time) is missing, the system shall prompt the patient to provide the missing information.
- The system shall converse with the patient **in French**, maintaining a polite and professional tone.

### 5.3 Scheduling
- The system shall parse the preferred time and convert it to a calendar event within the appropriate **timezone**.
- The system shall query the clinic’s calendar (e.g., **Google Calendar**) to check availability for the preferred time.
- If the requested time is unavailable, the system shall propose **up to two** alternative time slots.
- Upon confirmation by the patient, the system shall **create a calendar event** including the clinic and patient details.
- The system shall update both the clinic’s and the **patient’s calendars** with the new appointment.

### 5.4 Confirmations and Notifications
- The system shall send a **summary** of appointment details to the patient after booking.
- The system shall send a **reminder** to the patient **24 hours** before the appointment.
- The system shall allow the patient to **reschedule or cancel** an appointment via predefined keywords (e.g., “**modifier**” or “**annuler**”).

### 5.5 Rescheduling and Cancellation
- The system shall process **rescheduling** requests by checking the clinic’s calendar and offering new time options.
- The system shall process **cancellation** requests and remove the appointment from both calendars, notifying the clinic staff.
- The system shall **log** all rescheduling and cancellation actions for audit purposes.

### 5.6 Emergency Handling
- The system shall recognize urgent keywords (e.g., “**URGENT**”) and immediately **route the conversation to a human receptionist**.
- The system shall **notify clinic staff** of urgent messages via a designated communication channel (e.g., SMS or phone call).

### 5.7 Data Privacy and Security
- The system shall only collect and store **necessary data** for booking appointments.
- The system shall comply with **GDPR** requirements, including user consent and data deletion requests.
- The system shall **mask PII** (personally identifiable information) in logs and conversation history.
- Users may request **deletion** of their data via a keyword, and the system shall comply **within 24 hours**.

### 5.8 Logging and Monitoring
- The system shall **log all conversation interactions** and system actions for monitoring and troubleshooting.
- The system shall provide **traceability** for each appointment booking to evaluate performance and track metrics.
- **Monitoring tools** shall be used to ensure the system is running reliably and to detect any errors.

### 5.9 Internationalization
- The system shall support **French language** for all conversations with the patient.
- The system shall accommodate **time zone differences** between the clinic and the patient when scheduling appointments.
- Future versions shall allow **additional language support** and localization settings as needed.

## 6. Non‑Functional Requirements
- **Performance:** The system should respond to user messages within **5 seconds** on average.
- **Availability:** The system shall be available **24/7** to handle patient messages and bookings.
- **Scalability:** The system shall handle **multiple simultaneous conversations** and bookings without degradation of service.
- **Reliability:** The system shall provide **failover mechanisms**, including a fallback to human receptionists in case of system errors.
- **Security:** The system shall encrypt data **in transit and at rest**, and ensure user data is accessible only to authorized personnel.
- **Maintainability:** The system design should allow for easy updates and integration of new features or connectors.
- **Observability:** The system shall provide **monitoring and metrics** for performance, error rates, and usage analytics.

## 7. Assumptions and Constraints
- The prototype will integrate with **WhatsApp Business API** and **Google Calendar API** or equivalent services.
- The system will use an **orchestration framework** (e.g., **OpenAI Agent Builder** or **OpenAI Agents SDK**) to manage workflows.
- Users have a **WhatsApp‑enabled phone number** and a **valid email address** for calendar invitations.
- Initial deployment will target **French‑speaking patients** in the **Europe/Brussels** time zone.
- The system will operate under the **latest GDPR guidelines**, and data will be stored according to compliance requirements.
- **Clinic staff** will be trained to use the system and handle escalations.

## 8. Glossary
- **Agent Builder:** A visual tool for designing and deploying AI‑powered agent workflows using drag‑and‑drop nodes and connectors.
- **OpenAI Agents SDK:** A Python‑based SDK for building agentic workflows, with primitives for agents, handoffs, guardrails, and sessions.
- **Connector:** A module that facilitates integration with external services, such as Google Calendar or WhatsApp.
- **MCP (Model Context Protocol):** An open protocol that standardizes how applications provide context and tools to AI models.
- **Guardrail:** A safety mechanism that validates inputs and outputs to prevent undesired behavior, such as leaking sensitive information.

