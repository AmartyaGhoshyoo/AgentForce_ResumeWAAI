import os
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from crewai_tools import PDFSearchTool, DOCXSearchTool,SerperDevTool
import requests
import time 
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
        print(linkedin_url)
        response= requests.post(trigger_url, headers=headers, params=params, json=data).json()
        if 'snapshot_id' not in response:
            return {"error": "Could not trigger LinkedIn data collection"}
        progress_url = f"https://api.brightdata.com/datasets/v3/progress/{response['snapshot_id']}"
        snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{response['snapshot_id']}"
        print(response['snapshot_id'])
        time.sleep(30)
        max_attempts = 60  # Maximum 2 minutes (60 * 2 seconds)
        attempt = 0
        
        print(f"⏳ Waiting for LinkedIn data collection to complete...")
        
        while attempt < max_attempts:
            try:
                response_2=requests.get(progress_url,headers=headers)
                status_data = response_2.json()
                print(status_data)
                current_status = status_data.get('status', 'unknown')
                
                print(f"📊 Status check {attempt + 1}/{max_attempts}: {current_status}")
                
                if current_status == 'ready':
                    print("✅ Data collection completed!")
                    break
                elif current_status == 'failed':
                    return {
                        "error": "LinkedIn data collection failed", 
                        "status": status_data,
                        "details": status_data.get('error', 'Unknown error')
                    }
                elif current_status == 'error':
                    return {
                        "error": "LinkedIn data collection encountered an error", 
                        "status": status_data,
                        "details": status_data.get('error', 'Unknown error')
                    }
                
                # Wait 2 seconds before next poll
                time.sleep(30)
                attempt += 1
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Status check failed: {str(e)}")
                time.sleep(30)
                attempt += 1
                continue
        
        if attempt >= max_attempts:
            return {
                "error": "Timeout waiting for LinkedIn data collection to complete",
                "timeout_seconds": max_attempts * 2,
                "last_status": current_status if 'current_status' in locals() else 'unknown'
            }
        
        snap_params = {"format": "json"}
        snap_resp = requests.get(snapshot_url, headers=headers, params=snap_params).json()

        return snap_resp



url_data_fetcher = Agent(
    role="Digital Profile Data Collector",
    goal=(
        "Efficiently gather comprehensive professional data from online sources"
    "including resumes, GitHub repositories, and LinkedIn profiles to build a complete candidate profile"
    ),
    backstory=("You are an expert digital researcher with years of experience in talent acquisition technology. You specialize in extracting and organizing professional information from various online platforms."
               "Your expertise lies in understanding the nuances of different data sources and ensuring comprehensive data collection for career analysis."),
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
    goal=("Conduct comprehensive analysis of candidate profiles to identify missing technical skills, certifications, and competencies required for target positions"),
    backstory=("You are a senior technical recruiter and career counselor with 10+ years of experience in talent assessment."
               "You have deep knowledge of industry requirements across various tech roles and can quickly identify skill gaps. "
               "Your expertise includes understanding emerging technologies, industry trends, and the evolving demands of modern workplaces."),
    verbose=True,
    allow_delegation=False
)

experience_evaluator = Agent(
    role="Professional Experience Evaluator",
    goal="Assess candidate's professional experience, career progression, and alignment with target job requirements to identify experience gaps and growth opportunities",
    backstory=("You are an experienced career strategist and former hiring manager who has reviewed thousands of profiles."
               " You understand career trajectories, industry standards, and what makes candidates stand out."
               " Your analytical approach helps identify both strengths and areas for improvement in professional experience."),
    verbose=True,
    allow_delegation=False
)
job_search_agent = Agent(
    role="Job Search Specialist",
    goal=(
        "Find relevant job opportunities across multiple platforms including LinkedIn, Indeed, and Glassdoor,internshala,Unstop "
        "that match the candidate's profile, skills, and target requirements"
    ),
    backstory=(
        "You are an expert job search specialist with deep knowledge of recruitment platforms and job market trends. "
        "You have extensive experience in matching candidate profiles with relevant opportunities across various job boards. "
        "Your expertise lies in crafting targeted search queries, identifying high-quality opportunities, and understanding "
        "what makes a job posting attractive to specific candidate profiles."
    ),
    tools=[SerperDevTool()],
    verbose=True,
    allow_delegation=False
)

recruiter_feedback_specialist = Agent(
    role="Senior Talent Acquisition Consultant",
    goal=("Provide comprehensive, actionable feedback from a recruiter's perspective, "
          "including hiring recommendations, interview preparation advice, and career development suggestions"),
    backstory=("You are a senior executive recruiter with 15+ years of experience placing candidates in top-tier companies."
               " You have worked across multiple industries and understand what hiring managers look for."
               " Your feedback is direct, actionable, and focused on helping candidates improve their marketability and interview success rate."),
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
    **IMPORTANT**
    If one of them url is missing don't call tool for that missing one
    """,
    expected_output="A structured summary containing complete data from available sources: resume text, GitHub profile details with repository information, and LinkedIn professional data",
    agent=url_data_fetcher
)

# Updated File Processing Task
file_process_task = Task(
    description="""
    Process and analyze uploaded resume documents:
    
    **IMPORTANT: Check if uploaded_file_path is provided in the inputs**
    
    Uploaded file path: {uploaded_file_path}
    Target information: {target_input}
    Input type: {input_type}
    
    If uploaded_file_path is provided and not empty:
    1. Determine file type (PDF or DOCX) based on file extension
    2. Use appropriate tool to extract all text content from the file
    3. Identify and parse key sections:
       - Contact information (name, email, phone, location)
       - Professional summary/objective
       - Work experience (companies, roles, dates, responsibilities)
       - Education (degrees, institutions, graduation dates)
       - Technical skills and competencies
       - Certifications and licenses
       - Projects and achievements
       - Languages and additional skills
    4. Structure the information in a clear, organized format
    5. Highlight relevant keywords and phrases
    6. Note any gaps or areas that need clarification
    
    If no uploaded_file_path is provided or path is empty:
    - Return: "No resume file uploaded. Please upload a PDF or DOCX resume file for analysis."
    
    Focus on extracting comprehensive information that will be used for skills gap analysis and career guidance.
    """,
    expected_output="""
    If file is processed successfully:
    - Complete structured analysis of the uploaded resume including:
      * Candidate contact information
      * Professional summary
      * Detailed work experience with dates and responsibilities  
      * Educational background
      * Technical skills and tools
      * Certifications and achievements
      * Projects and portfolio items
      * Key strengths and areas of expertise
    
    If no file is uploaded:
    - Clear message indicating no file was provided for analysis
    """,
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

job_search_task = Task(
    description="""
    Search for relevant job opportunities based on the candidate profile and target requirements:
    
    Target information: {target_input}
    Input type: {input_type}
    Candidate skills and experience: [This will be populated from previous tasks]
    
    Search Strategy:
    1. Analyze the candidate's profile to identify key skills, experience level, and role preferences
    2. Create targeted search queries based on:
       - If Job Role/Title: Search for similar and related roles
       - If Job Description: Extract key requirements and search for matching positions
       - If Keywords: Use keywords to find relevant opportunities
    
    3. Search across multiple platforms:
       - LinkedIn Jobs (primary platform for professional roles)
       - Indeed (broad job market coverage)
       - Glassdoor (company insights and salary data)
    
    4. Filter and rank results by:
       - Relevance to candidate profile
       - Match with target requirements
       - Company reputation and growth potential
       - Salary range alignment
       - Location preferences
    
    5. Focus on finding:
       - Direct matches for target role
       - Adjacent opportunities that could be stepping stones
       - Companies known for hiring similar profiles
       - Remote/hybrid opportunities if applicable
    
    Return top 15-20 most relevant opportunities with direct application links.
    """,
    expected_output="""
    Curated list of job opportunities containing:
    - Job title and company name
    - Location and employment type
    - Salary range (if available)
    - Key requirements and qualifications
    - Match percentage with candidate profile
    - Direct application links
    - Platform source (LinkedIn, Indeed, Glassdoor)
    - Posted date and application deadline
    - Brief analysis of why this opportunity matches the candidate
    """,
    agent=job_search_agent
)

# Enhanced Recruiter Feedback Task with Job Opportunities Integration
recruiter_feedback_task = Task(
    description="""
    Provide comprehensive recruiter-style feedback, generate customized materials, and present relevant job opportunities based on target requirements:
    
    Target information: {target_input}
    Input type: {input_type}
    
    Feedback approach based on input type:
    - If Job Role/Title: Provide feedback specific to landing this type of role
    - If Job Description: Give detailed feedback on fit for this specific position
    - If Keywords: Focus feedback on how to strengthen alignment with these keywords/skills
    
    COMPREHENSIVE ANALYSIS AREAS:
    1. Overall candidate assessment and marketability for the target
    2. Specific strengths that make the candidate attractive
    3. Key weaknesses that could impact hiring decisions
    4. Resume and profile optimization recommendations including:
       - Missing keywords that should be incorporated
       - Experience gaps that need to be addressed or repositioned
       - Layout and formatting improvements for better ATS compatibility
       - Section restructuring recommendations
       - Quantification opportunities for achievements
    5. Interview preparation advice specific to the target
    6. Salary negotiation insights based on current profile
    7. Career development roadmap with timeline
    
    ADDITIONAL DELIVERABLES:
    8. Generate a customized cover letter template that:
       - Do not generate email look like cover letter
       - Generate Resume like format
       - Addresses specific requirements from the target job/role
       - Highlights relevant experience and skills from candidate profile
       - Uses appropriate tone and language for the target industry/role
       - Includes placeholders for company-specific customization
       - Demonstrates clear value proposition
    
    9. Simulate realistic recruiter feedback scenarios:
       - Initial resume screening feedback (pass/fail with reasons)
       - Phone screening talking points and potential questions
       - Interview panel recommendations
       - Reference check considerations
       - Negotiation positioning advice
    
    10. Actionable improvement checklist with priority levels:
        - High Priority: Critical issues that could eliminate candidacy
        - Medium Priority: Improvements that would strengthen positioning
        - Low Priority: Nice-to-have enhancements for competitive edge
    
    11. **RELEVANT JOB OPPORTUNITIES SECTION:**
        - Present job search results from the job_search_task
        - Categorize opportunities by fit level (Perfect Match, Good Match, Growth Opportunity)
        - Provide application strategy for each opportunity
        - Include direct clickable application links
        - Suggest customization points for each application
        - Prioritize opportunities based on candidate's current profile strength
    
    FORMATTING REQUIREMENTS:
    - Structure the response with clear sections and headers
    - Use bullet points for actionable items
    - Include specific examples and recommendations
    - Provide timeline estimates for improvements
    - **Format job opportunities as clickable links with clear call-to-action buttons**
    - Be direct, honest, and constructive in feedback
    - Focus on practical steps the candidate can implement immediately
    
    TONE: Professional yet approachable, direct but encouraging, focused on practical actionability rather than generic advice.
    """,
    expected_output="""
    A comprehensive recruiter assessment report containing:
    
    1. EXECUTIVE SUMMARY
       - Overall candidacy strength (1-10 scale)
       - Primary value propositions
       - Critical improvement areas
    
    2. DETAILED ANALYSIS
       - Strengths assessment with specific examples
       - Weakness identification with improvement strategies
       - Market positioning analysis
    
    3. RESUME OPTIMIZATION GUIDE
       - Keyword integration recommendations
       - Layout and formatting improvements
       - Content restructuring suggestions
       - ATS optimization tips
    
    4. CUSTOMIZED COVER LETTER TEMPLATE
       - In Resume format 
       - Tailored to target role/job description
       - Incorporates candidate's strongest selling points
       - Includes company customization placeholders
    
    5. INTERVIEW PREPARATION STRATEGY
       - Likely questions based on profile gaps
       - Recommended talking points
       - Story banking suggestions (STAR method examples)
    
    6. RECRUITER SIMULATION FEEDBACK
       - Initial screening assessment
       - Hiring manager perspective
       - Negotiation positioning advice
    
    7. PRIORITIZED ACTION PLAN
       - High/Medium/Low priority improvements
       - Timeline recommendations
       - Resource suggestions for skill development
    
    8. SALARY NEGOTIATION INSIGHTS
       - Market positioning assessment
       - Negotiation leverage points
       - Compensation discussion strategy
    
    9. **🎯 RELEVANT JOB OPPORTUNITIES**
       - **Perfect Match Jobs (90%+ fit)**: Direct application ready
       - **Good Match Jobs (70-89% fit)**: Minor improvements needed
       - **Growth Opportunities (50-69% fit)**: Stepping stone positions
       
       For each opportunity:
       - **[APPLY NOW]** - Direct clickable application link
       - Company name and role title
       - Key requirements match analysis
       - Salary range and benefits
       - Application deadline
       - Customization strategy for this specific role
       - Why this opportunity fits your profile
    
    10. **IMMEDIATE ACTION ITEMS**
        - Jobs to apply for this week
        - Profile improvements to make before applying
        - Companies to research and network with
        - Skills to highlight in applications
    """,
    agent=recruiter_feedback_specialist,
    context=[job_search_task]  # This ensures job search results are available
)

url_crew = Crew(
    agents=[url_data_fetcher, skills_gap_analyzer, experience_evaluator,job_search_agent, recruiter_feedback_specialist],
    tasks=[url_fetch_task, skills_analysis_task, experience_analysis_task, job_search_task,recruiter_feedback_task],
    verbose=True,
    sequential=True
)

file_crew = Crew(
    agents=[file_processor, skills_gap_analyzer, experience_evaluator,job_search_agent, recruiter_feedback_specialist],
    tasks=[file_process_task, skills_analysis_task, experience_analysis_task, job_search_task,recruiter_feedback_task],
    verbose=True,
    sequential=True
)
hybrid_crew = Crew(
    agents=[url_data_fetcher, file_processor, skills_gap_analyzer, experience_evaluator,job_search_agent, recruiter_feedback_specialist],
    tasks=[url_fetch_task, file_process_task, skills_analysis_task, experience_analysis_task, job_search_task,recruiter_feedback_task],
    verbose=True,
    sequential=True
)