from src.utils.logger import log_success, log_msg

def save_cold_message(cold_msg: str, hr_info: dict, job: dict, path: str) -> None:
    """Exports LinkedIn cold outreach script and HR/decision-maker discovery instructions to a text file."""
    log_msg(f"Saving LinkedIn cold message to: {path}...")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"COLD MESSAGE — {job.get('title', '')} at {job.get('company', '')}\n")
        f.write("=" * 60 + "\n\n")
        f.write("📩 LINKEDIN MESSAGE TO SEND:\n")
        f.write("-" * 40 + "\n")
        f.write(cold_msg.strip() + "\n\n")
        f.write("=" * 60 + "\n")
        f.write("🔍 HOW TO FIND HR AT THIS COMPANY:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Company       : {hr_info.get('company', 'Unknown')}\n")
        f.write(f"HR Search     : {hr_info.get('hr_search', '')}\n")
        f.write(f"Talent Search : {hr_info.get('talent_search', '')}\n")
        f.write(f"Founder/CTO   : {hr_info.get('founder_search', '')}\n\n")
        f.write("Look for people with these titles:\n")
        for role in hr_info.get("suggested_roles", []):
            f.write(f"  • {role}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("💡 OUTREACH STRATEGY:\n")
        f.write("-" * 40 + "\n")
        f.write("Step 1: Send connection request (no message yet)\n")
        f.write("Step 2: After they accept → send the cold message above\n")
        f.write("Step 3: No reply in 5 days → send ONE polite follow-up\n")
        f.write("Step 4: For startups → message the Founder/CTO directly\n")
        f.write("        (They respond faster than HR at small companies!)\n")
        f.write("\n⚠️  Personalize 1-2 lines per person — mention something\n")
        f.write("   specific about their company or recent work.\n")
        
    log_success(f"Cold message guide exported: {path}")


def save_interview_prep(interview_text: str, job: dict, path: str) -> None:
    """Exports custom interview preparation text content and checklist to a text file."""
    log_msg(f"Saving personalized interview preparation guide to: {path}...")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"INTERVIEW PREP — {job.get('title', '')} at {job.get('company', '')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(interview_text.strip())
        f.write("\n\n" + "=" * 60 + "\n")
        f.write("💡 PRE-INTERVIEW CHECKLIST:\n")
        f.write("-" * 40 + "\n")
        f.write("  □ Research the company — what do they build? Who are their customers?\n")
        f.write("  □ Push latest code to GitHub\n")
        f.write("  □ Deploy ClauseAI or have a screen recording ready\n")
        f.write("  □ Practice 30-second intro out loud 5 times\n")
        f.write("  □ Prepare 2 questions to ask the interviewer\n")
        f.write("  □ Test internet, mic, camera 30 min before\n")
        f.write("\n💬 QUESTIONS TO ASK THEM:\n")
        f.write("-" * 40 + "\n")
        f.write("  • What does a typical week look like for the intern?\n")
        f.write("  • What ML stack does the team use?\n")
        f.write("  • What's the biggest technical challenge the team is solving?\n")
        f.write("  • Is there a full-time opportunity after graduation?\n")
        
    log_success(f"Interview prep guide exported: {path}")
