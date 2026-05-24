import os
import re
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import settings
from src.utils.logger import (
    log_info, log_success, log_warning, log_error, 
    log_scrape, log_ai, log_email, log_trophy
)
from src.utils.resume_reader import read_resume
from src.utils.hr_finder import find_hr
from src.utils.mailer import send_email
from src.scoring.scorer import deduplicate, filter_stipend
from src.storage.seen_manager import load_seen, save_seen
from src.storage.pdf_generator import create_resume_pdf, create_cover_letter_pdf
from src.storage.file_exporter import save_cold_message, save_interview_prep
from src.llm.ollama_client import (
    rank_internships, generate_resume_content, 
    generate_cover_letter, generate_cold_message, prepare_interview
)
from src.scrapers import (
    scrape_internshala, scrape_linkedin, scrape_indeed, 
    scrape_naukri, scrape_wellfound, scrape_unstop, scrape_hackerearth
)

def run_pipeline() -> None:
    """Orchestrates the entire Internship Pipeline execution workflow."""
    
    # Visual pipeline header
    print("=" * 65)
    print("  ADITHYA'S ALL-IN-ONE INTERNSHIP PIPELINE v3.0 (Professional Edition)")
    print(f"  Platforms  : Internshala + LinkedIn + Indeed + Naukri")
    print(f"               + Wellfound + Unstop + HackerEarth (7 total!)")
    print(f"  AI Engine  : Ollama {settings.OLLAMA_MODEL} (FREE!)")
    print(f"  Locations  : {' + '.join(settings.LOCATIONS)}")
    print(f"  Stipend    : Rs.{settings.MIN_STIPEND}+/month")
    print(f"  Target     : ML Engineer / GenAI / LLM Engineer")
    print(f"  Cost       : Rs.0 FOREVER!")
    print("=" * 65)

    # 1. Read input resume text
    resume_text = read_resume()

    # 2. Load seen internships database
    seen_urls = load_seen()

    # 3. Scrape all 7 platforms
    all_listings = []
    try:
        all_listings += scrape_internshala()
        all_listings += scrape_linkedin()
        all_listings += scrape_indeed()
        all_listings += scrape_naukri()
        all_listings += scrape_wellfound()
        all_listings += scrape_unstop()
        all_listings += scrape_hackerearth()
    except Exception as ex:
        log_error(f"Unexpected error during scraping phase: {ex}")

    log_info(f"Total raw listings discovered across platforms: {len(all_listings)}")

    # 4. Deduplicate listings based on normalized Title and Company name
    unique_listings = deduplicate(all_listings)

    # 5. Filter by minimum stipend range (or unspecified)
    filtered_listings = filter_stipend(unique_listings)
    
    if not filtered_listings:
        log_warning("No internship listings matched the stipend filter. Exiting pipeline.")
        return

    # 6. Use local Ollama instance to analyze and rank the matches
    ranked_text, new_urls, top_jobs = rank_internships(
        filtered_listings, seen_urls, resume_text
    )
    
    if not ranked_text:
        log_success("No NEW internship opportunities found since the last run. Check back tomorrow!")
        return

    print("\n" + "=" * 65)
    log_trophy("AI TOP PICKS FOR ML ENGINEER:")
    print("=" * 65)
    print(ranked_text)

    # 7. Extract the top recommendation to generate tailored collateral
    top_job = top_jobs[0]
    log_success(f"Tailoring documents for TOP MATCH: {top_job['title']} at {top_job['company']} ({top_job['location']})")

    # Generate a safe filesystem slug from company name
    safe_company_name = re.sub(r"[^a-zA-Z0-9]", "_", top_job["company"])[:15]

    # 8. Leverage Ollama to generate highly tailored content
    tailored_resume_bullets = generate_resume_content(resume_text, top_job)
    tailored_cover_letter = generate_cover_letter(resume_text, top_job)
    cold_outreach_msg = generate_cold_message(top_job)
    interview_cheat_sheet = prepare_interview(top_job)
    hr_search_queries = find_hr(top_job)

    # 9. Establish output file paths (saving inside outputs/ directory)
    resume_out = os.path.join(settings.OUTPUTS_DIR, f"Resume_Adithya_{safe_company_name}.pdf")
    cover_out = os.path.join(settings.OUTPUTS_DIR, f"CoverLetter_Adithya_{safe_company_name}.pdf")
    cold_out = os.path.join(settings.OUTPUTS_DIR, f"ColdMessage_Adithya_{safe_company_name}.txt")
    interview_out = os.path.join(settings.OUTPUTS_DIR, f"InterviewPrep_Adithya_{safe_company_name}.txt")

    # 10. Generate and write the output files to disk
    create_resume_pdf(tailored_resume_bullets, top_job, resume_out)
    create_cover_letter_pdf(tailored_cover_letter, top_job, cover_out)
    save_cold_message(cold_outreach_msg, hr_search_queries, top_job, cold_out)
    save_interview_prep(interview_cheat_sheet, top_job, interview_out)

    # 11. Send summary email with all 4 custom documents attached
    send_email(
        job=top_job,
        ranked_text=ranked_text,
        resume_path=resume_out,
        cover_path=cover_out,
        cold_msg_path=cold_out,
        interview_path=interview_out
    )

    # 12. Save newly seen URLs to avoid repeat processing in subsequent runs
    seen_urls.update(new_urls)
    save_seen(seen_urls)

    # Final summary output
    print("\n" + "=" * 65)
    log_success("ALL DONE! Pipeline completed successfully!")
    log_info(f"Tailored Resume     : {os.path.basename(resume_out)} (Saved to outputs/)")
    log_info(f"Tailored Cover Letter: {os.path.basename(cover_out)} (Saved to outputs/)")
    log_info(f"Cold Outreach Script : {os.path.basename(cold_out)} (Saved to outputs/)")
    log_info(f"Interview Cheat Sheet: {os.path.basename(interview_out)} (Saved to outputs/)")
    log_info(f"Alert Dispatch Status: Delivered to {settings.RECEIVER_EMAIL}")
    print("=" * 65)
    print("\n  📅 Run again tomorrow for fresh internships!")
    print("  💡 Automation Tip — schedule daily execution:")
    print("     Linux/Mac: crontab -e  →  0 9 * * * python main.py")
    print("     Windows  : Task Scheduler → trigger daily at 9:00 AM")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline execution aborted by user.")
        sys.exit(0)
    except Exception as e:
        log_error(f"Pipeline crashed with an unhandled exception: {e}")
        sys.exit(1)
