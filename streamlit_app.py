import streamlit as st
import tempfile
import os
from crewai_setup import url_crew, file_crew, hybrid_crew

st.set_page_config(
    page_title="AI Career Assistant", 
    page_icon="🚀", 
    layout="wide"
)

st.title("🚀 AI-Powered Career Assistant")
st.markdown("Get comprehensive career analysis and recruiter feedback to boost your job prospects!")

# Sidebar for inputs
st.sidebar.title("📋 Profile Input Options")

# Input method selection
input_method = st.sidebar.radio(
    "Choose your input method:",
    ["URLs Only", "File Upload Only" ] #"Both URLs and Files"
)

# Initialize variables
resume_url = None
github_url = None
linkedin_url = None
uploaded_file = None
target_job_role = None

# Target job role (common for all methods)
target_job_role = st.sidebar.text_input(
    "🎯 Target Job Role/Position", 
    placeholder="e.g., Senior Software Engineer, Data Scientist, Product Manager"
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

if input_method in ["File Upload Only"]:
    st.sidebar.subheader("📁 File Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume", 
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )

# Analysis options
st.sidebar.subheader("⚙️ Analysis Options")
include_github = st.sidebar.checkbox("Include GitHub Analysis", value=True)
include_linkedin = st.sidebar.checkbox("Include LinkedIn Analysis", value=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔍 How it works:")
    st.markdown("""
    1. **Data Collection**: Our AI agents fetch your professional data from various sources
    2. **Skills Analysis**: Identify gaps in technical and soft skills for your target role
    3. **Experience Evaluation**: Assess your career progression and experience alignment
    4. **Recruiter Feedback**: Get honest, actionable feedback from an AI recruiter perspective
    """)

with col2:
    st.markdown("### 📊 What you'll get:")
    st.markdown("""
    - ✅ Skills gap analysis
    - ✅ Experience evaluation
    - ✅ Resume optimization tips
    - ✅ Interview preparation advice
    - ✅ Career development roadmap
    """)

# Run analysis button
if st.sidebar.button("🚀 Run Career Analysis", type="primary"):
    # Validation
    has_input = False
    
    if input_method in ["URLs Only"]:
        if resume_url or github_url or linkedin_url:
            has_input = True
    
    if input_method in ["File Upload Only"]:
        if uploaded_file:
            has_input = True
    
    if not has_input:
        st.sidebar.error("❌ Please provide at least one input source!")
        st.stop()
    
    if not target_job_role:
        st.sidebar.warning("⚠️ Target job role will help provide more specific feedback!")
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Determine which crew to use
        crew_to_use = None
        inputs = {"target_job_role": target_job_role or "General Professional Role"}
        
        if input_method == "URLs Only":
            crew_to_use = url_crew
            inputs.update({
                "resume_url": resume_url,
                "github_url": github_url if include_github else None,
                "linkedin_url": linkedin_url if include_linkedin else None
            })
            
        elif input_method == "File Upload Only":
            crew_to_use = file_crew
            # Handle file upload
            if uploaded_file:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    inputs["uploaded_file_path"] = tmp_file.name
                    
        else:  # Both URLs and Files
            crew_to_use = hybrid_crew
            inputs.update({
                "resume_url": resume_url,
                "github_url": github_url if include_github else None,
                "linkedin_url": linkedin_url if include_linkedin else None
            })
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    inputs["uploaded_file_path"] = tmp_file.name
        
        # Update progress
        progress_bar.progress(25)
        status_text.text("🔄 Initializing AI agents...")
        
        # Run the analysis
        progress_bar.progress(50)
        status_text.text("🤖 AI agents are analyzing your profile...")
        
        result = crew_to_use.kickoff(inputs=inputs)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Display results
        st.success("🎉 Career Analysis Complete!")
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Skills Analysis", "💼 Experience Review", "👨‍💼 Recruiter Feedback"])
        
        with tab1:
            st.markdown("### 📋 Analysis Summary")
            st.write(result)
        
        with tab2:
            st.markdown("### 🎯 Skills Gap Analysis")
            st.info("Detailed skills analysis will be shown here based on the AI agent's findings.")
        
        with tab3:
            st.markdown("### 📈 Experience Evaluation")
            st.info("Professional experience assessment will be displayed here.")
        
        with tab4:
            st.markdown("### 💡 Recruiter Insights")
            st.info("Recruiter feedback and recommendations will be shown here.")
        
        # Cleanup temporary files
        if 'uploaded_file_path' in inputs and os.path.exists(inputs['uploaded_file_path']):
            os.unlink(inputs['uploaded_file_path'])
            
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        
        # Cleanup on error
        if 'uploaded_file_path' in locals() and 'uploaded_file_path' in inputs:
            if os.path.exists(inputs['uploaded_file_path']):
                os.unlink(inputs['uploaded_file_path'])

# Footer
st.markdown("---")
st.markdown("**💡 Tips for better results:**")
st.markdown("""
- Ensure your GitHub profile is public and showcases relevant projects
- Use a comprehensive LinkedIn profile with detailed experience descriptions  
- Provide a well-formatted resume with clear sections
- Specify your target job role for more targeted feedback
""")

# Additional features
with st.expander("🔧 Advanced Settings"):
    st.markdown("**Coming Soon:**")
    st.markdown("- Industry-specific analysis")
    st.markdown("- Salary benchmarking")
    st.markdown("- Interview question preparation")
    st.markdown("- ATS compatibility check")