import os
import requests
from crewai import Agent, Task
from crewai.tools import BaseTool
from typing import Dict, List
import json

class JobSearchTool(BaseTool):
    name: str = "job_search"
    description: str = "Search for job opportunities across multiple platforms including LinkedIn, Indeed, Glassdoor using SerpAPI"

    def _run(self, query: str, location: str = "", num_results: int = 10, platforms: List[str] = None) -> Dict:
        """
        Search for jobs using SerpAPI across multiple platforms
        
        Args:
            query: Job search query (role, skills, keywords)
            location: Job location (city, state, country)
            num_results: Number of results to return (default: 10)
            platforms: List of platforms to search ['linkedin', 'indeed', 'glassdoor']
        """
        if platforms is None:
            platforms = ['linkedin', 'indeed', 'glassdoor']
        
        api_key = os.getenv('SERPER_API_KEY')
        if not api_key:
            return {"error": " SERPER_API_KEY not found in environment variables"}
        
        all_jobs = []
        
        # Search LinkedIn Jobs
        if 'linkedin' in platforms:
            linkedin_jobs = self._search_linkedin_jobs(query, location, num_results, api_key)
            all_jobs.extend(linkedin_jobs.get('jobs', []))
        
        # Search Indeed Jobs
        if 'indeed' in platforms:
            indeed_jobs = self._search_indeed_jobs(query, location, num_results, api_key)
            all_jobs.extend(indeed_jobs.get('jobs', []))
        
        # Search Glassdoor Jobs
        if 'glassdoor' in platforms:
            glassdoor_jobs = self._search_glassdoor_jobs(query, location, num_results, api_key)
            all_jobs.extend(glassdoor_jobs.get('jobs', []))
        
        # Remove duplicates and sort by relevance
        unique_jobs = self._deduplicate_jobs(all_jobs)
        sorted_jobs = sorted(unique_jobs, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            "total_jobs_found": len(sorted_jobs),
            "jobs": sorted_jobs[:num_results],
            "search_query": query,
            "location": location,
            "platforms_searched": platforms
        }

    def _search_linkedin_jobs(self, query: str, location: str, num_results: int, api_key: str) -> Dict:
        """Search LinkedIn jobs using SerpAPI"""
        params = {
            "engine": "linkedin_jobs",
            "keywords": query,
            "location_name": location,
            "api_key": api_key,
            "start": 0
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get('jobs', [])[:num_results]:
                jobs.append({
                    "title": job.get('title', 'N/A'),
                    "company": job.get('company', 'N/A'),
                    "location": job.get('location', 'N/A'),
                    "description": job.get('description', 'N/A'),
                    "apply_link": job.get('apply_link', ''),
                    "posted_date": job.get('posted_at', 'N/A'),
                    "employment_type": job.get('employment_type', 'N/A'),
                    "seniority_level": job.get('seniority_level', 'N/A'),
                    "platform": "LinkedIn",
                    "job_id": job.get('job_id', ''),
                    "relevance_score": self._calculate_relevance(job, query)
                })
            
            return {"jobs": jobs, "platform": "LinkedIn"}
            
        except Exception as e:
            return {"error": f"LinkedIn search failed: {str(e)}", "jobs": []}

    def _search_indeed_jobs(self, query: str, location: str, num_results: int, api_key: str) -> Dict:
        """Search Indeed jobs using SerpAPI"""
        params = {
            "engine": "indeed_jobs",
            "q": query,
            "l": location,
            "api_key": api_key,
            "start": 0
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get('jobs_results', [])[:num_results]:
                jobs.append({
                    "title": job.get('title', 'N/A'),
                    "company": job.get('company_name', 'N/A'),
                    "location": job.get('location', 'N/A'),
                    "description": job.get('description', 'N/A'),
                    "apply_link": job.get('apply_link', ''),
                    "posted_date": job.get('posted_at', 'N/A'),
                    "employment_type": job.get('detected_extensions', {}).get('schedule', 'N/A'),
                    "salary": job.get('salary', 'N/A'),
                    "platform": "Indeed",
                    "job_id": job.get('job_id', ''),
                    "relevance_score": self._calculate_relevance(job, query)
                })
            
            return {"jobs": jobs, "platform": "Indeed"}
            
        except Exception as e:
            return {"error": f"Indeed search failed: {str(e)}", "jobs": []}

    def _search_glassdoor_jobs(self, query: str, location: str, num_results: int, api_key: str) -> Dict:
        """Search Glassdoor jobs using SerpAPI"""
        params = {
            "engine": "glassdoor_jobs",
            "keyword": query,
            "location": location,
            "api_key": api_key,
            "start": 0
        }
        
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get('jobs', [])[:num_results]:
                jobs.append({
                    "title": job.get('title', 'N/A'),
                    "company": job.get('company', 'N/A'),
                    "location": job.get('location', 'N/A'),
                    "description": job.get('description', 'N/A'),
                    "apply_link": job.get('apply_url', ''),
                    "posted_date": job.get('posted_time', 'N/A'),
                    "salary": job.get('salary', 'N/A'),
                    "rating": job.get('rating', 'N/A'),
                    "platform": "Glassdoor",
                    "job_id": job.get('job_id', ''),
                    "relevance_score": self._calculate_relevance(job, query)
                })
            
            return {"jobs": jobs, "platform": "Glassdoor"}
            
        except Exception as e:
            return {"error": f"Glassdoor search failed: {str(e)}", "jobs": []}

    def _calculate_relevance(self, job: Dict, query: str) -> float:
        """Calculate relevance score based on title and description match"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        query_words = query.lower().split()
        
        score = 0
        for word in query_words:
            if word in title:
                score += 3  # Higher weight for title matches
            if word in description:
                score += 1  # Lower weight for description matches
        
        return score

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.get('title', '').lower(), job.get('company', '').lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    
tool=JobSearchTool()
result=tool.run('SDE','Delhi')
print(result)