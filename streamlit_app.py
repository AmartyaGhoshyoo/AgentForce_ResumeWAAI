import streamlit as st
import tempfile
import os
import re
from Main_Server import url_crew, file_crew, hybrid_crew

st.set_page_config(
    page_title="AI Career Assistant", 
    page_icon="🚀", 
    layout="wide"
)

st.title("🚀 AI-Powered Career Assistant")
st.caption("Developed by Amartya Ghosh an AI Developer 👨🏻‍💻")
st.markdown("Get comprehensive career analysis and recruiter feedback to boost your job prospects!")
st.sidebar.title("📋 Profile Input Options")
input_method = st.sidebar.radio(
    "Choose your input method:",
    ["URLs Only", "File Upload Only", "Both URLs and Files"]
)
resume_url = None
github_url = None
linkedin_url = None
uploaded_file = None
target_input = None
st.sidebar.subheader("🎯 Target Position Details")
input_type = st.sidebar.radio(
    "What would you like to provide?",
    ["Job Role/Title", "Job Description", "Keywords/Skills"]
)

if input_type == "Job Role/Title":
    target_input = st.sidebar.text_input(
        "Job Role/Position", 
        placeholder="e.g., Senior Software Engineer, Data Scientist, Product Manager"
    )
elif input_type == "Job Description":
    target_input = st.sidebar.text_area(
        "Job Description",
        placeholder="Paste the complete job description here...",
        height=200
    )
else:
    target_input = st.sidebar.text_area(
        "Target Keywords/Skills",
        placeholder="e.g., Python, Machine Learning, AWS, Agile, Leadership, React, Node.js",
        height=100
    )
if input_method in ["URLs Only"]:
    st.sidebar.subheader("🔗 Profile URLs")
    resume_url = st.sidebar.text_input(
        "Resume URL (PDF/Google Drive)", 
        placeholder="https://drive.google.com/file/d/..."
    )
    github_url = st.sidebar.text_input(
        "GitHub Profile URL", 
        placeholder="https://github.com/username"
    )
    linkedin_url = st.sidebar.text_input(
        "LinkedIn Profile URL", 
        placeholder="https://linkedin.com/in/username"
    )
    st.sidebar.subheader("⚙️ Analysis Options")
    include_github = st.sidebar.checkbox("Include GitHub Analysis", value=True,key='git')
    include_linkedin = st.sidebar.checkbox("Include LinkedIn Analysis", value=True,key='lin')

if input_method in ["File Upload Only"]:
    st.sidebar.subheader("📁 File Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume", 
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
   
if input_method in ["Both URLs and Files"]:
    st.sidebar.subheader("📁 File Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume", 
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
        
    )
    st.sidebar.subheader("🔗 Profile URLs")
    resume_url = st.sidebar.text_input(
        "Resume URL (PDF/Google Drive)", 
        placeholder="https://drive.google.com/file/d/..."
    )
    github_url = st.sidebar.text_input(
        "GitHub Profile URL", 
        placeholder="https://github.com/username"
    )
    linkedin_url = st.sidebar.text_input(
        "LinkedIn Profile URL", 
        placeholder="https://linkedin.com/in/username"
    )
    st.sidebar.subheader("⚙️ Analysis Options")
    include_github = st.sidebar.checkbox("Include GitHub Analysis", value=True,key='gith')
    include_linkedin = st.sidebar.checkbox("Include LinkedIn Analysis", value=True,key='link')

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔍 How it works:")
    st.markdown("""
    1. **Data Collection**: My AI agents fetch your professional data from various sources
    2. **Smart Analysis**: AI adapts analysis based on your target (role, JD, or keywords)
    3. **Skills Gap Identification**: Identify missing technical and soft skills
    4. **Experience Evaluation**: Assess career progression and alignment
    5. **Recruiter Feedback**: Get honest, actionable feedback from an AI recruiter
    """)

with col2:
    st.markdown("### 📊 What you'll get:")
    st.markdown("""
    - ✅ Tailored skills gap analysis
    - ✅ Experience evaluation
    - ✅ Resume optimization tips
    - ✅ Interview preparation advice
    - ✅ Career development roadmap
    - ✅ Target-specific recommendations
    """)
st.markdown("### 🎯 Target Input Types:")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    **Job Role/Title** 🎯
    - Quick analysis for specific positions
    - Industry standard comparisons
    - Role-focused recommendations
    """)

with col_b:
    st.markdown("""
    **Job Description** 📄
    - Most comprehensive analysis
    - Exact requirement matching
    - Position-specific optimization
    """)

with col_c:
    st.markdown("""
    **Keywords/Skills** 🔑
    - Skill-focused assessment
    - Targeted learning paths
    - Keyword optimization
    """)

if st.sidebar.button("🚀 Run Career Analysis", type="primary"):
    has_input = False
    
    if input_method in ["URLs Only", "Both URLs and Files"]:
        if resume_url or github_url or linkedin_url:
            has_input = True
    
    if input_method in ["File Upload Only", "Both URLs and Files"]:
        if uploaded_file:
            has_input = True
    
    if not has_input:
        st.sidebar.error("❌ Please provide at least one input source!")
        st.stop()
    
    if not target_input:
        st.sidebar.warning("⚠️ Target information will help provide more specific feedback!")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        crew_to_use = None
        inputs = {
            "target_input": target_input or "General Professional Position",
            "input_type": input_type
        }
        
        if input_method == "URLs Only":
            crew_to_use = url_crew
            inputs.update({
                "resume_url": resume_url or "",
                "github_url": github_url if include_github else "",
                "linkedin_url": linkedin_url if include_linkedin else ""
            })
            
        elif input_method == "File Upload Only":
            crew_to_use = file_crew
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    inputs["uploaded_file_path"] = tmp_file.name
            else:
                st.sidebar.error("❌ Please upload a file!")
                st.stop()
                
        else: 
            crew_to_use = hybrid_crew
            inputs.update({
                "resume_url": resume_url or "",
                "github_url": github_url if include_github else "",
                "linkedin_url": linkedin_url if include_linkedin else ""
            })
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    inputs["uploaded_file_path"] = tmp_file.name
        progress_bar.progress(25)
        status_text.text("🔄 Initializing AI agents...")
        
        st.info(f"🎯 **Analysis Target**: {input_type} - {target_input[:100]}{'...' if len(target_input) > 100 else ''}")
        
        progress_bar.progress(50)
        status_text.text("🤖 AI agents are analyzing your profile...")
        
        result = crew_to_use.kickoff(inputs=inputs)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        st.success("🎉 Career Analysis Complete!")
        st.markdown(f"### 📋 Analysis Results for: {input_type}")
        if input_type == "Job Role/Title":
            st.markdown(f"**Target Role**: {target_input}")
        elif input_type == "Job Description":
            st.markdown(f"**Job Description Analysis** (First 200 chars): {target_input[:200]}...")
        else:
            st.markdown(f"**Target Keywords**: {target_input}")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Complete Analysis", 
            "🎯 Skills Gap", 
            "💼 Experience Review", 
            "👨‍💼 Recruiter Feedback",
            "📈 Action Plan"
        ])
        
        with tab1:
            st.markdown("### 📋 Complete Analysis Summary")
            if hasattr(result, 'raw'):
                st.write(result.raw)
            else:
                st.write(str(result))
        
        with tab2:
            st.markdown("### 🎯 Skills Gap Analysis")
            st.info("🔍 **Skills analysis based on your target requirements**")
            pattern = r'(.*\s*3\..*?\n)(.*?)(\n.*\s*4\..*)'
        
            match = re.search(pattern, result.raw, re.S)
            

            if match:
                print('this is tab2')
                points_inside_3 = match.group(2).strip()
                print("\nPoints inside 3:\n", points_inside_3)
                st.write(points_inside_3)
            
            st.markdown("*Skills gap analysis extracted from the complete analysis above.*")
        
        with tab3:
            st.markdown("### 📈 Experience Evaluation")
            st.info("💼 **Professional experience assessment**")
            pattern = r'(.*\s*2\..*?\n)(.*?)(\n.*\s*3\..*)'
    
            match = re.search(pattern, result.raw, re.S)
            if match:
                print("this is tab3")
                points_inside_2 = match.group(2).strip()
                print("\nPoints inside 2:\n", points_inside_2)
                st.write(points_inside_2)
            st.markdown("*Experience evaluation extracted from the complete analysis above.*")
        
        with tab4:
            st.markdown("### 💡 Recruiter Insights")
            st.info("👨‍💼 **Recruiter perspective and recommendations**")
            pattern = r'(.*\s*6\..*?\n)(.*?)(\n.*\s*7\..*)'
            match = re.search(pattern, result.raw, re.S)

            if match:
                points_inside_6 = match.group(2).strip()
                print("\nPoints inside 6:\n", points_inside_6)
                st.write(points_inside_6)
            st.markdown("*Recruiter feedback extracted from the complete analysis above.*")
            
        with tab5:
            pattern = r'(.*\s*7\..*?\n)(.*?)(\n.*\s*8\..*)'
            match = re.search(pattern, result.raw, re.S)
            if match:
                points_inside_7 = match.group(2).strip()
                print("\nPoints inside 7:\n", points_inside_7)
                st.write(points_inside_7)

        if 'uploaded_file_path' in inputs and os.path.exists(inputs['uploaded_file_path']):
            os.unlink(inputs['uploaded_file_path'])
            
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        
        with st.expander("🔍 Error Details (for debugging)"):
            st.code(str(e))
        
        if 'uploaded_file_path' in inputs and os.path.exists(inputs['uploaded_file_path']):
            os.unlink(inputs['uploaded_file_path'])

st.markdown("---")
st.markdown("### 💡 Tips for Better Results:")

tip_col1, tip_col2 = st.columns(2)

with tip_col1:
    st.markdown("""
    **For Job Role Analysis:**
    - Be specific (e.g., "Senior Frontend Developer" vs "Developer")
    - Include seniority level
    - Mention specific technologies if relevant
    
    **For GitHub Analysis:**
    - Ensure your profile is public
    - Pin your best repositories
    - Add detailed README files
    """)

with tip_col2:
    st.markdown("""
    **For Job Description Analysis:**
    - Copy the complete job posting
    - Include requirements and nice-to-haves
    - Don't edit or summarize the JD
    
    **For LinkedIn Analysis:**
    - Keep your profile updated
    - Add detailed experience descriptions
    - Include relevant skills and endorsements
    """)
with st.expander("🔧 Advanced Settings & Features"):
    st.markdown("### 🚀 Coming Soon:")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        **Analysis Enhancements:**
        - Industry-specific analysis
        - Company culture fit assessment
        - Salary benchmarking
        - ATS compatibility check
        """)
    
    with feature_col2:
        st.markdown("""
        **Career Tools:**
        - Interview question preparation
        - Mock interview practice
        - Portfolio optimization
        - Career path visualization
        """)
    
    st.markdown("### 🎯 Current Analysis Capabilities:")
    st.markdown("""
    - ✅ Multi-format target input (Role/JD/Keywords)
    - ✅ Comprehensive profile data collection
    - ✅ AI-powered skills gap analysis
    - ✅ Professional experience evaluation
    - ✅ Expert recruiter feedback
    - ✅ Personalized action planning
    """)