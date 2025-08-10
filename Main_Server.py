import os
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from crewai_tools import PDFSearchTool, DOCXSearchTool
import requests
import fitz
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

class ResumeFetcherTool(BaseTool):
    name: str = "resume_fetcher"
    description: str = "Fetch resume text from a PDF URL or Google Drive link."

    def _run(self, url: str) -> str:
        url = self._convert_drive_link(url)
        r = requests.get(url)
        r.raise_for_status()
        pdf_bytes = BytesIO(r.content)

        text = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _convert_drive_link(self, link):
        import re
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return link


class GithubFetcherTool(BaseTool):
    name: str = "github_fetcher"
    description: str = "Fetch public GitHub profile and repositories from a GitHub profile URL."

    def _run(self, github_url: str) -> dict:
        username = github_url.strip("/").split("/")[-1]
        headers = {}
        gh_token = os.getenv("GH_TOKEN")
        if gh_token:
            headers["Authorization"] = f"token {gh_token}"

        profile = requests.get(f"https://api.github.com/users/{username}", headers=headers).json()
        repos = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers, params={"per_page": 100}).json()

        return {
            "profile": profile,
            "repos": [
                {
                    "name": r.get("name"),
                    "description": r.get("description"),
                    "language": r.get("language"),
                    "stars": r.get("stargazers_count")
                }
                for r in repos if isinstance(r, dict)
            ]
        }


class LinkedInFetcherTool(BaseTool):
    name: str = "linkedin_data_fetcher"
    description: str = "Fetch public LinkedIn profile data."

    def _run(self, linkedin_url: str) -> dict:
        trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
        headers = {
            "Authorization": f"Bearer {os.getenv('Bright')}",
            "Content-Type": "application/json",
        }
        params = {
            "dataset_id": "gd_l1viktl72bvl7bjuj0",
            "include_errors": "true",
        }
        data = [{"url": linkedin_url}]
        response= requests.post(trigger_url, headers=headers, params=params, json=data).json()

        snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{response['snapshot_id']}"
        response_2=requests.get(snapshot_url,headers=headers)
        while (response_2['status']!='ready'):
            continue
        snap_params = {"format": "json"}
        snap_resp = requests.get(snapshot_url, headers=headers, params=snap_params).json()

        return snap_resp



url_data_fetcher = Agent(
    role="Digital Profile Data Collector",
    goal=("Efficiently gather comprehensive professional data from online sources,"
    "including resumes, GitHub repositories, and LinkedIn profiles to build a complete candidate profile")
    backstory=("You are an expert digital researcher with years of experience in talent acquisition technology. You specialize in extracting and organizing professional information from various online platforms."
               "Your expertise lies in understanding the nuances of different data sources and ensuring comprehensive data collection for career analysis.",)
    tools=[ResumeFetcherTool(), GithubFetcherTool(), LinkedInFetcherTool()],
    verbose=True,
    allow_delegation=False
)

file_processor = Agent(
    role="Document Analysis Specialist",
    goal="Extract and analyze content from uploaded resume documents (PDF/DOCX) to understand candidate qualifications, skills, and experience",
    backstory="You are a seasoned document processing expert with deep knowledge in parsing professional documents. You have extensive experience in extracting meaningful information from resumes, cover letters, and professional portfolios. Your analytical skills help identify key competencies, achievements, and career progression patterns.",
    tools=[PDFSearchTool(), DOCXSearchTool()],
    verbose=True,
    allow_delegation=False
)


skills_gap_analyzer = Agent(
    role="Technical Skills Gap Analyst",
    goal=("Conduct comprehensive analysis of candidate profiles to identify missing technical skills, certifications, and competencies required for target positions",)
    backstory=("You are a senior technical recruiter and career counselor with 10+ years of experience in talent assessment."
               "You have deep knowledge of industry requirements across various tech roles and can quickly identify skill gaps. "
               "Your expertise includes understanding emerging technologies, industry trends, and the evolving demands of modern workplaces.",)
    verbose=True,
    allow_delegation=False
)

experience_evaluator = Agent(
    role="Professional Experience Evaluator",
    goal="Assess candidate's professional experience, career progression, and alignment with target job requirements to identify experience gaps and growth opportunities",
    backstory=("You are an experienced career strategist and former hiring manager who has reviewed thousands of profiles."
               " You understand career trajectories, industry standards, and what makes candidates stand out."
               " Your analytical approach helps identify both strengths and areas for improvement in professional experience.",)
    verbose=True,
    allow_delegation=False
)

recruiter_feedback_specialist = Agent(
    role="Senior Talent Acquisition Consultant",
    goal="Provide comprehensive, actionable feedback from a recruiter's perspective, including hiring recommendations, interview preparation advice, and career development suggestions",
    backstory="You are a senior executive recruiter with 15+ years of experience placing candidates in top-tier companies. You have worked across multiple industries and understand what hiring managers look for. Your feedback is direct, actionable, and focused on helping candidates improve their marketability and interview success rate.",
    verbose=True,
    allow_delegation=False
)

url_fetch_task = Task(
    description="""
    Fetch and compile comprehensive professional data from any of the provided online sources:
    1. Extract complete resume text from the PDF URL if provided: {resume_url}
    2. Gather GitHub profile information if URL provided: {github_url}
    3. Collect LinkedIn profile data if URL provided: {linkedin_url}
    
    Target information: {target_input}
    Input type: {input_type}
    
    Handle cases where URLs might be empty or invalid gracefully.
    """,
    expected_output="A structured summary containing complete data from available sources: resume text, GitHub profile details with repository information, and LinkedIn professional data",
    agent=url_data_fetcher
)

file_process_task = Task(
    description="""
    Process and analyze uploaded resume documents:
    1. Extract all text content from uploaded PDF or DOCX files
    2. Identify key sections (experience, education, skills, projects)
    3. Parse and structure the information for analysis
    
    Target information: {target_input}
    Input type: {input_type}
    
    Focus on extracting: contact information, work experience, education, technical skills, certifications, projects, and achievements.
    """,
    expected_output="Structured analysis of the uploaded resume including all key professional information organized by categories",
    agent=file_processor
)

skills_analysis_task = Task(
    description="""
    Conduct a thorough skills gap analysis based on the collected candidate data and target requirements:
    
    Target information: {target_input}
    Input type: {input_type}
    
    Analysis approach based on input type:
    - If Job Role/Title: Research industry standards and requirements for this specific role
    - If Job Description: Extract specific requirements, skills, and qualifications from the provided JD
    - If Keywords: Focus analysis around the provided keywords and skills
    
    1. Identify current technical skills, tools, and technologies from candidate data
    2. Compare against target requirements
    3. Highlight missing critical skills and certifications
    4. Suggest specific learning paths and resources
    5. Prioritize skills based on market demand and career impact
    
    Consider both hard technical skills and soft skills relevant to the position.
    """,
    expected_output="Detailed skills gap analysis report with prioritized recommendations for skill development and specific learning resources",
    agent=skills_gap_analyzer
)

experience_analysis_task = Task(
    description="""
    Evaluate the candidate's professional experience and career progression against target requirements:
    
    Target information: {target_input}
    Input type: {input_type}
    
    Analysis approach based on input type:
    - If Job Role/Title: Compare experience against typical requirements for this role level
    - If Job Description: Match experience against specific requirements mentioned in the JD
    - If Keywords: Assess how well current experience aligns with the target keywords/skills
    
    1. Assess career trajectory and growth pattern
    2. Identify experience gaps for target requirements
    3. Evaluate project complexity and impact
    4. Analyze leadership and collaboration experiences
    5. Compare experience level against target expectations
    
    Provide insights on how to better position existing experience and what additional experience is needed.
    """,
    expected_output="Comprehensive experience evaluation with specific recommendations for strengthening professional background",
    agent=experience_evaluator
)

recruiter_feedback_task = Task(
    description="""
    Provide comprehensive recruiter-style feedback based on target requirements:
    
    Target information: {target_input}
    Input type: {input_type}
    
    Feedback approach based on input type:
    - If Job Role/Title: Provide feedback specific to landing this type of role
    - If Job Description: Give detailed feedback on fit for this specific position
    - If Keywords: Focus feedback on how to strengthen alignment with these keywords/skills
    
    Cover the following areas:
    1. Overall candidate assessment and marketability for the target
    2. Specific strengths that make the candidate attractive
    3. Key weaknesses that could impact hiring decisions
    4. Resume and profile optimization recommendations
    5. Interview preparation advice specific to the target
    6. Salary negotiation insights based on current profile
    7. Career development roadmap with timeline
    
    Be direct, honest, and actionable in your feedback. Focus on practical steps the candidate can take immediately.
    """,
    expected_output="Professional recruiter assessment with actionable recommendations for immediate and long-term career improvement",
    agent=recruiter_feedback_specialist
)

url_crew = Crew(
    agents=[url_data_fetcher, skills_gap_analyzer, experience_evaluator, recruiter_feedback_specialist],
    tasks=[url_fetch_task, skills_analysis_task, experience_analysis_task, recruiter_feedback_task],
    verbose=True,
    sequential=True
)

file_crew = Crew(
    agents=[file_processor, skills_gap_analyzer, experience_evaluator, recruiter_feedback_specialist],
    tasks=[file_process_task, skills_analysis_task, experience_analysis_task, recruiter_feedback_task],
    verbose=True,
    sequential=True
)
hybrid_crew = Crew(
    agents=[url_data_fetcher, file_processor, skills_gap_analyzer, experience_evaluator, recruiter_feedback_specialist],
    tasks=[url_fetch_task, file_process_task, skills_analysis_task, experience_analysis_task, recruiter_feedback_task],
    verbose=True,
    sequential=True
)