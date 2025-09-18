"""
Job Posting API Service

This module provides integration with job posting APIs to fetch real job data.
Currently supports JSearch API (RapidAPI) and can be extended for other services.
"""

import requests
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Represents a job posting from an external API."""
    
    job_id: str
    title: str
    company: str
    location: str
    description: str
    job_url: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    employment_type: Optional[str] = None
    remote: bool = False
    posted_date: Optional[datetime] = None
    source: str = "unknown"
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job posting to dictionary."""
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'job_url': self.job_url,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'employment_type': self.employment_type,
            'remote': self.remote,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'source': self.source,
            'requirements': self.requirements or [],
            'benefits': self.benefits or []
        }
    
    def get_salary_range(self) -> Optional[str]:
        """Get formatted salary range string."""
        if self.salary_min and self.salary_max:
            currency = self.salary_currency or 'USD'
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f} {currency}"
        elif self.salary_min:
            currency = self.salary_currency or 'USD'
            return f"${self.salary_min:,.0f}+ {currency}"
        return None


class JobAPIError(Exception):
    """Custom exception for job API errors."""
    pass


class JobSearchAPI:
    """Base class for job search API implementations."""
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Search for jobs. To be implemented by subclasses."""
        raise NotImplementedError
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information. To be implemented by subclasses."""
        raise NotImplementedError


class JSearchAPI(JobSearchAPI):
    """JSearch API implementation (RapidAPI)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize JSearch API client."""
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        if not self.api_key:
            logger.warning("No RapidAPI key found. Set RAPIDAPI_KEY environment variable.")
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Search for jobs using JSearch API."""
        if not self.api_key:
            logger.error("No API key available for job search")
            return []
        
        try:
            search_query = query
            if location:
                search_query += f" in {location}"
            
            params = {
                "query": search_query,
                "page": "1",
                "num_pages": "1",
                "date_posted": "all"
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            job_data = data.get("data", [])[:limit]
            
            for job in job_data:
                try:
                    job_posting = self._parse_job_data(job)
                    if job_posting:
                        jobs.append(job_posting)
                except Exception as e:
                    logger.warning(f"Error parsing job data: {e}")
                    continue
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise JobAPIError(f"Failed to search jobs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during job search: {e}")
            raise JobAPIError(f"Job search failed: {e}")
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information."""
        if not self.api_key:
            logger.error("No API key available for job details")
            return None
        
        try:
            params = {"job_id": job_id}
            
            response = requests.get(
                f"{self.base_url}/job-details",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            job_data = data.get("data", [])
            if job_data:
                return self._parse_job_data(job_data[0])
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting job details: {e}")
            return None
    
    def _parse_job_data(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse job data from API response."""
        try:
            # Extract salary information
            salary_min = None
            salary_max = None
            salary_currency = None
            
            if job_data.get("job_salary_period"):
                salary_min = job_data.get("job_min_salary")
                salary_max = job_data.get("job_max_salary")
                salary_currency = job_data.get("job_salary_currency", "USD")
            
            # Parse posted date
            posted_date = None
            if job_data.get("job_posted_at_datetime_utc"):
                try:
                    posted_date = datetime.fromisoformat(
                        job_data["job_posted_at_datetime_utc"].replace('Z', '+00:00')
                    )
                except:
                    pass
            
            # Extract requirements and benefits
            requirements = []
            benefits = []
            
            description = job_data.get("job_description", "")
            if "requirements" in description.lower():
                # Simple extraction - could be enhanced with NLP
                requirements = ["See job description for detailed requirements"]
            
            if "benefits" in description.lower():
                benefits = ["See job description for detailed benefits"]
            
            return JobPosting(
                job_id=job_data["job_id"],
                title=job_data.get("job_title", ""),
                company=job_data.get("employer_name", ""),
                location=f"{job_data.get('job_city', '')}, {job_data.get('job_state', '')}, {job_data.get('job_country', '')}".strip(', '),
                description=job_data.get("job_description", ""),
                job_url=job_data.get("job_apply_link", ""),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=salary_currency,
                employment_type=job_data.get("job_employment_type", ""),
                remote=job_data.get("job_is_remote", False),
                posted_date=posted_date,
                source="JSearch",
                requirements=requirements,
                benefits=benefits
            )
            
        except KeyError as e:
            logger.error(f"Missing required field in job data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing job data: {e}")
            return None


class MockJobAPI(JobSearchAPI):
    """Mock job API for testing and development when no API key is available."""
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Return mock job postings for testing."""
        logger.info(f"Using mock job data for query: {query}")
        
        mock_jobs = [
            JobPosting(
                job_id="mock_001",
                title="Senior Python Developer",
                company="Tech Solutions Inc",
                location="San Francisco, CA, USA",
                description="We are looking for a Senior Python Developer to join our team. Experience with Flask, Django, and API development required.",
                job_url="https://example.com/job/1",
                salary_min=120000,
                salary_max=160000,
                salary_currency="USD",
                employment_type="Full-time",
                remote=True,
                posted_date=datetime.now(),
                source="Mock",
                requirements=["Python", "Flask", "Django", "API Development"],
                benefits=["Health Insurance", "401k", "Remote Work"]
            ),
            JobPosting(
                job_id="mock_002",
                title="Full Stack Engineer",
                company="StartupCorp",
                location="Austin, TX, USA",
                description="Join our fast-growing startup! Looking for a full-stack engineer with React and Node.js experience.",
                job_url="https://example.com/job/2",
                salary_min=90000,
                salary_max=130000,
                salary_currency="USD",
                employment_type="Full-time",
                remote=False,
                posted_date=datetime.now(),
                source="Mock",
                requirements=["React", "Node.js", "JavaScript", "MongoDB"],
                benefits=["Equity", "Flexible Hours", "Free Lunch"]
            ),
            JobPosting(
                job_id="mock_003",
                title="Data Scientist",
                company="Analytics Pro",
                location="New York, NY, USA",
                description="Data Scientist position focusing on machine learning and predictive analytics. Python and R experience preferred.",
                job_url="https://example.com/job/3",
                salary_min=110000,
                salary_max=150000,
                salary_currency="USD",
                employment_type="Full-time",
                remote=True,
                posted_date=datetime.now(),
                source="Mock",
                requirements=["Python", "R", "Machine Learning", "Statistics"],
                benefits=["Health Insurance", "Dental", "Vision", "401k"]
            )
        ]
        
        # Filter based on query (simple matching)
        filtered_jobs = []
        query_lower = query.lower()
        
        for job in mock_jobs[:limit]:
            if (query_lower in job.title.lower() or 
                query_lower in job.description.lower() or
                any(req.lower() in query_lower for req in job.requirements or [])):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Return mock job details."""
        # Return the first mock job for any ID
        mock_jobs = self.search_jobs("", "", 1)
        return mock_jobs[0] if mock_jobs else None


class JobAPIService:
    """Main service class for job API operations."""
    
    def __init__(self, use_mock: bool = False):
        """Initialize job API service."""
        self.use_mock = use_mock
        
        if use_mock or not os.getenv('RAPIDAPI_KEY'):
            logger.info("Using mock job API")
            self.api = MockJobAPI()
        else:
            logger.info("Using JSearch API")
            self.api = JSearchAPI()
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Search for jobs."""
        try:
            return self.api.search_jobs(query, location, limit)
        except Exception as e:
            logger.error(f"Job search failed, falling back to mock data: {e}")
            mock_api = MockJobAPI()
            return mock_api.search_jobs(query, location, limit)
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get job details."""
        try:
            return self.api.get_job_details(job_id)
        except Exception as e:
            logger.error(f"Failed to get job details: {e}")
            return None
    
    def job_to_application_data(self, job: JobPosting) -> Dict[str, Any]:
        """Convert job posting to application data format."""
        return {
            'company': job.company,
            'position': job.title,
            'job_url': job.job_url,
            'salary_range': job.get_salary_range(),
            'location': job.location,
            'notes': f"Applied via job posting API\nSource: {job.source}\nJob ID: {job.job_id}\nEmployment Type: {job.employment_type or 'Not specified'}\n\nRequirements: {', '.join(job.requirements or ['See job description'])}\n\nBenefits: {', '.join(job.benefits or ['See job description'])}",
            'job_posting_id': job.job_id,
            'job_posting_source': job.source
        }


# Convenience function for easy import
def get_job_service(use_mock: bool = False) -> JobAPIService:
    """Get a job API service instance."""
    return JobAPIService(use_mock=use_mock)
