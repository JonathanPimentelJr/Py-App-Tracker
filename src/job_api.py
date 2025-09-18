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


class AdzunaAPI(JobSearchAPI):
    """Adzuna API implementation - Free tier available."""
    
    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize Adzuna API client."""
        self.app_id = app_id or os.getenv('ADZUNA_APP_ID')
        self.api_key = api_key or os.getenv('ADZUNA_API_KEY')
        self.base_url = "https://api.adzuna.com/v1/api"
        
        if not self.app_id or not self.api_key:
            logger.warning("No Adzuna API credentials found. Set ADZUNA_APP_ID and ADZUNA_API_KEY environment variables.")
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Search for jobs using Adzuna API."""
        if not self.app_id or not self.api_key:
            logger.error("No API credentials available for Adzuna job search")
            return []
        
        try:
            # Adzuna uses country-specific endpoints
            country = "us"  # Default to US, could be configurable
            
            params = {
                "app_id": self.app_id,
                "app_key": self.api_key,
                "results_per_page": min(limit, 50),
                "what": query,
                "content-type": "application/json"
            }
            
            if location:
                params["where"] = location
            
            response = requests.get(
                f"{self.base_url}/jobs/{country}/search/1",
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            results = data.get("results", [])
            
            for job in results:
                try:
                    job_posting = self._parse_adzuna_job(job)
                    if job_posting:
                        jobs.append(job_posting)
                except Exception as e:
                    logger.warning(f"Error parsing Adzuna job data: {e}")
                    continue
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API request failed: {e}")
            raise JobAPIError(f"Failed to search jobs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Adzuna job search: {e}")
            raise JobAPIError(f"Job search failed: {e}")
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information from Adzuna."""
        # Adzuna doesn't have a separate job details endpoint
        # The search results already contain detailed information
        return None
    
    def _parse_adzuna_job(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse job data from Adzuna API response."""
        try:
            # Extract salary information
            salary_min = job_data.get("salary_min")
            salary_max = job_data.get("salary_max")
            
            # Parse created date
            posted_date = None
            if job_data.get("created"):
                try:
                    posted_date = datetime.fromisoformat(job_data["created"].replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract location info
            location_parts = []
            area = job_data.get("location", {})
            if isinstance(area, dict):
                if area.get("display_name"):
                    location_parts.append(area["display_name"])
            else:
                location_parts.append(str(area))
            
            location = ", ".join(filter(None, location_parts))
            
            # Extract company info
            company = job_data.get("company", {}).get("display_name", "Unknown Company")
            
            return JobPosting(
                job_id=str(job_data.get("id", "")),
                title=job_data.get("title", ""),
                company=company,
                location=location,
                description=job_data.get("description", ""),
                job_url=job_data.get("redirect_url", ""),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency="USD",
                employment_type=job_data.get("contract_type", ""),
                remote=False,  # Adzuna doesn't clearly indicate remote
                posted_date=posted_date,
                source="Adzuna",
                requirements=[],
                benefits=[]
            )
            
        except Exception as e:
            logger.error(f"Error parsing Adzuna job data: {e}")
            return None


class USAJobsAPI(JobSearchAPI):
    """USAJobs.gov API implementation - Completely free for US government jobs."""
    
    def __init__(self, email: Optional[str] = None):
        """Initialize USAJobs API client."""
        self.email = email or os.getenv('USAJOBS_EMAIL') or "pyapptracker@example.com"
        self.base_url = "https://data.usajobs.gov/api"
        # USAJobs API requires specific headers
        self.headers = {
            "User-Agent": f"PyAppTracker/1.0 (Contact: {self.email})",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Search for jobs using USAJobs API."""
        try:
            params = {
                "Keyword": query,
                "ResultsPerPage": min(limit, 500),
                "Page": 1
            }
            
            if location:
                params["LocationName"] = location
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            results = data.get("SearchResult", {}).get("SearchResultItems", [])
            
            for item in results:
                try:
                    job_data = item.get("MatchedObjectDescriptor", {})
                    job_posting = self._parse_usajobs_data(job_data)
                    if job_posting:
                        jobs.append(job_posting)
                except Exception as e:
                    logger.warning(f"Error parsing USAJobs data: {e}")
                    continue
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"USAJobs API request failed: {e}")
            raise JobAPIError(f"Failed to search jobs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during USAJobs search: {e}")
            raise JobAPIError(f"Job search failed: {e}")
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed job information from USAJobs."""
        # USAJobs search already provides detailed information
        return None
    
    def _parse_usajobs_data(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse job data from USAJobs API response."""
        try:
            # Extract salary information
            salary_min = None
            salary_max = None
            
            position_remuneration = job_data.get("PositionRemuneration", [])
            if position_remuneration:
                salary_info = position_remuneration[0]
                salary_min = salary_info.get("MinimumRange")
                salary_max = salary_info.get("MaximumRange")
            
            # Parse dates
            posted_date = None
            if job_data.get("PublicationStartDate"):
                try:
                    posted_date = datetime.fromisoformat(
                        job_data["PublicationStartDate"].replace('Z', '+00:00')
                    )
                except:
                    pass
            
            # Extract location
            locations = job_data.get("PositionLocation", [])
            location_parts = []
            for loc in locations[:2]:  # Take first 2 locations
                city = loc.get("CityName", "")
                state = loc.get("StateCode", "")
                if city and state:
                    location_parts.append(f"{city}, {state}")
            
            location = "; ".join(location_parts) or "USA"
            
            # Check for remote work
            remote = any(
                loc.get("CityName", "").lower() in ["anywhere", "remote", "telework"]
                for loc in locations
            )
            
            return JobPosting(
                job_id=job_data.get("PositionID", ""),
                title=job_data.get("PositionTitle", ""),
                company=job_data.get("OrganizationName", "US Government"),
                location=location,
                description=job_data.get("UserArea", {}).get("Details", {}).get("MajorDuties", [""])[0] if job_data.get("UserArea", {}).get("Details", {}).get("MajorDuties") else job_data.get("QualificationSummary", ""),
                job_url=job_data.get("ApplyURI", [""])[0] if job_data.get("ApplyURI") else "",
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency="USD",
                employment_type="Full-time",
                remote=remote,
                posted_date=posted_date,
                source="USAJobs.gov",
                requirements=job_data.get("QualificationSummary", "").split("\n")[:3] if job_data.get("QualificationSummary") else [],
                benefits=["Federal Benefits Package", "Health Insurance", "Retirement Plan"]
            )
            
        except Exception as e:
            logger.error(f"Error parsing USAJobs data: {e}")
            return None


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
    
    def __init__(self, use_mock: bool = False, preferred_api: str = "auto"):
        """Initialize job API service with multiple API support."""
        self.use_mock = use_mock
        self.apis = []
        self.current_api = None
        
        if use_mock:
            logger.info("Using mock job API")
            self.apis = [MockJobAPI()]
        else:
            # Initialize APIs in priority order (free first)
            self._initialize_apis(preferred_api)
        
        self.current_api = self.apis[0] if self.apis else None
    
    def _initialize_apis(self, preferred_api: str):
        """Initialize available APIs in priority order."""
        available_apis = []
        
        # Check USAJobs.gov API (completely free)
        try:
            usa_api = USAJobsAPI()
            available_apis.append(('usajobs', usa_api))
            logger.info("✅ USAJobs.gov API initialized (Free)")
        except Exception as e:
            logger.warning(f"USAJobs API initialization failed: {e}")
        
        # Check Adzuna API (free tier)
        if os.getenv('ADZUNA_APP_ID') and os.getenv('ADZUNA_API_KEY'):
            try:
                adzuna_api = AdzunaAPI()
                available_apis.append(('adzuna', adzuna_api))
                logger.info("✅ Adzuna API initialized (Free Tier)")
            except Exception as e:
                logger.warning(f"Adzuna API initialization failed: {e}")
        
        # Check JSearch API (RapidAPI - paid)
        if os.getenv('RAPIDAPI_KEY'):
            try:
                jsearch_api = JSearchAPI()
                available_apis.append(('jsearch', jsearch_api))
                logger.info("✅ JSearch API initialized (RapidAPI)")
            except Exception as e:
                logger.warning(f"JSearch API initialization failed: {e}")
        
        # Sort APIs based on preference
        if preferred_api != "auto" and preferred_api:
            # Move preferred API to front
            available_apis.sort(key=lambda x: x[0] != preferred_api)
        
        self.apis = [api for _, api in available_apis]
        
        # Only use mock as absolute last resort
        if not self.apis:
            logger.warning("No external APIs available, will use mock data only as final fallback")
            # Don't add MockJobAPI here - let it be added only when absolutely necessary
    
    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[JobPosting]:
        """Search for jobs using multiple APIs with fallback."""
        all_jobs = []
        
        # If no APIs configured, immediately use mock
        if not self.apis:
            logger.warning("No external APIs configured, using mock data")
            mock_api = MockJobAPI()
            return mock_api.search_jobs(query, location, limit)
        
        jobs_per_api = max(1, limit // len(self.apis)) if len(self.apis) > 1 else limit
        
        # Try each configured API
        for i, api in enumerate(self.apis):
            try:
                api_name = api.__class__.__name__
                logger.info(f"Trying {api_name} for job search...")
                
                jobs = api.search_jobs(query, location, jobs_per_api)
                if jobs:
                    all_jobs.extend(jobs)
                    logger.info(f"✅ {api_name} returned {len(jobs)} jobs")
                    
                    # If we have enough jobs, we can stop here
                    if len(all_jobs) >= limit:
                        break
                else:
                    logger.warning(f"⚠️ {api_name} returned no jobs for query: {query}")
                    
            except Exception as e:
                api_name = api.__class__.__name__
                logger.error(f"❌ {api_name} failed: {e}")
                continue
        
        # Only use mock if absolutely no real results found
        if not all_jobs:
            logger.warning(f"All external APIs failed to return jobs for '{query}', using mock data as final fallback")
            mock_api = MockJobAPI()
            try:
                all_jobs = mock_api.search_jobs(query, location, limit)
                logger.info(f"📝 Mock API provided {len(all_jobs)} sample jobs")
            except Exception as e:
                logger.error(f"Even mock API failed: {e}")
                return []
        
        # Return up to the requested limit
        return all_jobs[:limit]
    
    def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get job details from multiple APIs."""
        for api in self.apis:
            try:
                api_name = api.__class__.__name__
                job = api.get_job_details(job_id)
                if job:
                    logger.info(f"✅ {api_name} returned job details")
                    return job
            except Exception as e:
                api_name = api.__class__.__name__
                logger.error(f"❌ {api_name} failed to get job details: {e}")
                continue
        
        logger.error(f"Failed to get job details for ID: {job_id}")
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
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get status of all configured APIs."""
        status = {
            'total_apis': len(self.apis),
            'current_api': self.current_api.__class__.__name__,
            'available_apis': [],
            'recommendations': []
        }
        
        for api in self.apis:
            api_info = {
                'name': api.__class__.__name__,
                'type': 'Mock' if isinstance(api, MockJobAPI) else 'External',
                'cost': 'Free' if isinstance(api, (USAJobsAPI, MockJobAPI)) else 'Free Tier' if isinstance(api, AdzunaAPI) else 'Paid'
            }
            status['available_apis'].append(api_info)
        
        # Add recommendations
        if not any(isinstance(api, USAJobsAPI) for api in self.apis):
            status['recommendations'].append("Consider using USAJobs.gov API (completely free for US government jobs)")
        
        if not any(isinstance(api, AdzunaAPI) for api in self.apis):
            status['recommendations'].append("Consider signing up for Adzuna API (free tier available)")
        
        if len([api for api in self.apis if not isinstance(api, MockJobAPI)]) == 0:
            status['recommendations'].append("No external APIs configured. Using mock data only.")
        
        return status


# Convenience function for easy import
def get_job_service(use_mock: bool = False) -> JobAPIService:
    """Get a job API service instance."""
    return JobAPIService(use_mock=use_mock)
