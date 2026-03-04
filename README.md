# Job Bot

A tool that helps you apply to jobs with less manual work: you upload your resume once, the agent reads it and saves it; jobs come from your **LinkedIn notifications (bell icon)**; the agent fetches those jobs, chooses which to apply to (based on your resume and preferences), and can apply for you (via LinkedIn Easy Apply or by logging into ATS sites like Workday and filling forms).

---

## High-Level Idea

1. **User uploads resume once** (separate upload button, not in chat). The agent parses it (PDF → text → Gemini → structured data), validates it, and saves it. This is the single source of truth for “what the agent knows about the user.”
2. **Jobs are not searched by the agent.** They already appear in the **user’s LinkedIn notifications** (the **bell icon**). The agent’s job is to **fetch** that list — not to search the internet.
3. **Job Detector** uses the user’s **LinkedIn credentials** to access LinkedIn, open the bell/notifications section, and extract the list of job postings and their URLs. That list goes into the database (Job table).
4. **Prioritization:** When the agent has a bunch of jobs from the bell, it **chooses which job to apply to** (and in what order) using the parsed resume and some preferences (to be defined later). So: “which job first” = agent uses resume + job descriptions to order/filter the list.
5. **Applying:**
   - If the job can be applied to **through LinkedIn** (e.g. Easy Apply), the agent uses that when possible.
   - If applying redirects to an **external ATS site** (e.g. Workday):  
     - **User has login** (email/password for that site) → agent logs in, fills questions/resume/details, and applies.  
     - **User doesn’t have an account** → agent sends a **notification** (e.g. “Create an account on Workday”) so the user can create an ID; then we can retry or use it next time.
6. **Credentials:** The agent uses the **user’s LinkedIn credentials** to access LinkedIn (bell + Easy Apply). For ATS sites (Workday, Greenhouse, etc.), we store site-specific credentials so the agent can log in and fill forms. We can decide exact storage (e.g. same credential table with `site="linkedin"` or `site="workday"`) as we build.

**Single user for now:** One resume, one LinkedIn, one set of credentials. Multi-user/auth can be considered later.

---

## How Different Backend Parts Fit

| Part | Purpose |
|------|--------|
| **`api/routes/resume.py`** | Entry point for “upload resume” (POST `/resume/upload`) and “get current resume” (GET `/resume` when added). |
| **`ai/resume_parser.py`** | Read the resume: PDF → text (PyMuPDF) → Gemini → structured JSON → validate → save/load. |
| **`ai/gemini.py`** | Calls Gemini API (e.g. for resume parsing; later for prioritizer or other agent steps). |
| **`models/job.py`** | Job table: where the **Job Detector** stores jobs fetched from LinkedIn notifications (company, role, apply_url, ATS type, etc.). |
| **`models/application.py`** | Application table: record each application (status: applied / failed / action_needed, result, screenshot, etc.). |
| **`models/credential.py`** | Store LinkedIn and ATS logins (site, username, password_encrypted) for detector and Application Engine. |
| **Job Detector** (e.g. `bot/detector.py`) | *To build.* Uses LinkedIn credentials → open bell/notifications → extract jobs + URLs → write to Job table. |
| **JD Fetcher** | *To build.* Given a job URL, fetch full job description (role, skills, internship/full-time, etc.). |
| **Pipeline / Prioritizer** | *To build.* Uses parsed resume + job list + job descriptions to decide which job to apply to first (and which to skip). |
| **Application Engine** | *To build.* Uses parsed resume + credentials to fill ATS forms (and LinkedIn Easy Apply when possible). |

**Resume flow (already implemented):** User uploads PDF → `resume.py` → `resume_parser.py` (extract text, Gemini, validate) → save to `uploads/parsed_resume.json`. Same data is used later for prioritization and for filling application forms.

---

## What’s Built vs Planned

- **Done:** Resume upload and parsing (`resume.py`, `resume_parser.py`, `gemini.py`). DB models and app skeleton (`main.py`, CORS, `init_db`). Resume router is not yet mounted in `main.py` (commented out).
- **To do:** Mount resume router; add GET `/resume`; Job Detector; JD Fetcher; pipeline/prioritizer; Application Engine; frontend (e.g. ChatGPT-like UI with separate resume upload button); credential storage and usage; notifications for “create an ID” when user has no ATS account.

---

## Setup (after cloning)

1. **Backend**
   - `cd backend`
   - Create and activate a virtualenv: `python -m venv venv`, then activate (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on macOS/Linux).
   - `pip install -r requirements.txt`
   - Add a `.env` (e.g. copy from `backend.env` if present) with at least `GEMINI_API_KEY`; optionally `DATABASE_URL`, `FRONTEND_URL`.
   - Run from `backend`: `uvicorn main:app --reload` (or `python -m uvicorn main:app --reload`). Ensure you are in the `backend` directory so that `uploads/` and imports resolve correctly.

2. **Frontend**  
   Not built yet; CORS is set for `http://localhost:5173` (e.g. Vite default).

---

## Design Notes (for future sessions)

- **Resume:** One-time upload via a **separate upload button**; no need to upload again and again.
- **Jobs source:** Only the **LinkedIn bell (notifications)**. Agent fetches that list; it does not search for jobs.
- **“Which job first”:** Agent uses the **parsed resume** and job info to choose order/filter from the list from the bell.
- **Apply:** Prefer LinkedIn Easy Apply; otherwise go to ATS (e.g. Workday). With ATS credentials → auto-apply; without → notify user to create an ID.
- **LinkedIn access:** Agent uses the **user’s LinkedIn credentials** to read the bell and (when possible) apply via LinkedIn.

---

*Last updated to reflect project state and design as of current development. Details (e.g. “resolve” step in pipeline, exact credential schema) can be decided as we build.*
