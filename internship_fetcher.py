"""
Real-time Internship Fetcher
Scrapes Indeed, LinkedIn, Naukri.com, and Internshala for internships matching student profile.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urlencode

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

PLATFORM_LOGOS = {
    'indeed': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Indeed_logo.svg/200px-Indeed_logo.svg.png',
    'linkedin': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/200px-LinkedIn_logo_initials.png',
    'naukri': 'https://img.icons8.com/color/48/naukri.png',
    'internshala': 'https://img.icons8.com/color/48/internshala.png',
}


class InternshipFetcher:
    """Fetches live internships from multiple platforms."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_all(self, query: str = '', location: str = '', skills: List[str] = None,
                  max_per_platform: int = 10) -> List[Dict[str, Any]]:
        """Fetch internships from all platforms and return unified results."""
        search_query = query or self._build_query_from_skills(skills or [])

        all_results = []
        fetchers = [
            ('indeed', self._fetch_indeed),
            ('linkedin', self._fetch_linkedin),
            ('naukri', self._fetch_naukri),
            ('internshala', self._fetch_internshala),
        ]

        for platform, fetcher in fetchers:
            try:
                results = fetcher(search_query, location, max_per_platform)
                for r in results:
                    r['platform'] = platform
                    r['platform_logo'] = PLATFORM_LOGOS.get(platform, '')
                all_results.extend(results)
                logger.info(f"Fetched {len(results)} internships from {platform}")
            except Exception as e:
                logger.warning(f"Failed to fetch from {platform}: {e}")

        return all_results

    def _build_query_from_skills(self, skills: List[str]) -> str:
        """Convert student skills into a search query."""
        if not skills:
            return 'internship'
        priority_skills = skills[:3]
        return ' '.join(priority_skills) + ' internship'

    def _fetch_indeed(self, query: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape Indeed for internship listings."""
        results = []
        params = {
            'q': query,
            'l': location or 'India',
            'fromage': 14,
            'start': 0,
        }
        url = f"https://in.indeed.com/jobs?{urlencode(params)}"

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            cards = soup.select('div.job_seen_beacon') or soup.select('div.jobsearch-ResultsList > div') or []

            for card in cards[:max_results]:
                try:
                    title_el = card.select_one('h2.jobTitle a') or card.select_one('a[data-jk]')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title:
                        continue

                    company_el = card.select_one('span[data-testid="company-name"]') or card.select_one('span.companyName')
                    company = company_el.get_text(strip=True) if company_el else 'Unknown'

                    location_el = card.select_one('div[data-testid="text-location"]') or card.select_one('div.companyLocation')
                    loc = location_el.get_text(strip=True) if location_el else location or 'India'

                    snippet_el = card.select_one('div.job-snippet') or card.select_one('table.jobCardShelfContainer')
                    snippet = snippet_el.get_text(' ', strip=True)[:200] if snippet_el else ''

                    salary_el = card.select_one('div.salary-snippet-container') or card.select_one('span.estimated-salary')
                    salary = salary_el.get_text(strip=True) if salary_el else 'Not specified'

                    link = ''
                    if title_el and title_el.get('href'):
                        link = f"https://in.indeed.com{title_el['href']}" if title_el['href'].startswith('/') else title_el['href']

                    results.append({
                        'title': title,
                        'company': company,
                        'location': loc,
                        'description': snippet,
                        'stipend': salary,
                        'apply_url': link or f"https://in.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location or 'India')}",
                        'posted': 'Recent',
                        'skills_extracted': self._extract_skills_from_text(title + ' ' + snippet),
                    })
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"Indeed fetch error: {e}")

        return results

    def _fetch_linkedin(self, query: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape LinkedIn job search for internships."""
        results = []
        params = {
            'keywords': query,
            'location': location or 'India',
            'f_TPR': 'r604800',
            'position': '1',
            'pageNum': '0',
        }
        url = f"https://www.linkedin.com/jobs/search?{urlencode(params)}"

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            cards = soup.select('li') or []

            count = 0
            for card in cards:
                if count >= max_results:
                    break
                try:
                    title_el = card.select_one('h3.base-search-card__title') or card.select_one('a.job-card-container__link')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title:
                        continue

                    company_el = card.select_one('h4.base-search-card__subtitle') or card.select_one('a.hidden-nested-link')
                    company = company_el.get_text(strip=True) if company_el else 'Unknown'

                    location_el = card.select_one('span.job-search-card__location')
                    loc = location_el.get_text(strip=True) if location_el else location or 'India'

                    link_el = card.select_one('a.base-card__full-link') or card.select_one('a[href*="/jobs/"]')
                    link = link_el['href'] if link_el and link_el.get('href') else ''

                    time_el = card.select_one('time')
                    posted = time_el.get_text(strip=True) if time_el else 'Recent'

                    desc_el = card.select_one('p') or card.select_one('div.job-search-card__snippets')
                    desc = desc_el.get_text(strip=True)[:200] if desc_el else ''

                    results.append({
                        'title': title,
                        'company': company,
                        'location': loc,
                        'description': desc,
                        'stipend': 'Check listing',
                        'apply_url': link or f"https://www.linkedin.com/jobs/search?keywords={quote_plus(query)}",
                        'posted': posted,
                        'skills_extracted': self._extract_skills_from_text(title + ' ' + desc),
                    })
                    count += 1
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"LinkedIn fetch error: {e}")

        return results

    def _fetch_naukri(self, query: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape Naukri.com for internship listings."""
        results = []
        params = {
            'keyword': query,
            'location': location or 'India',
            'jobType': 'internship',
        }
        url = f"https://www.naukri.com/internships-jobs?{urlencode(params)}"

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            cards = soup.select('div.styles_jd-header__BqfOH') or soup.select('article.tuple') or soup.select('div.srp-cardlisting')

            for card in cards[:max_results]:
                try:
                    title_el = card.select_one('a.title') or card.select_one('h2 a') or card.select_one('a[href*="naukri.com"]')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title:
                        continue

                    company_el = card.select_one('a.subTitle') or card.select_one('span.companyName')
                    company = company_el.get_text(strip=True) if company_el else 'Unknown'

                    location_el = card.select_one('span.location') or card.select_one('li.location')
                    loc = location_el.get_text(strip=True) if location_el else location or 'India'

                    desc_el = card.select_one('span.jobDescription') or card.select_one('div.job-desc')
                    desc = desc_el.get_text(strip=True)[:200] if desc_el else ''

                    link = ''
                    if title_el and title_el.get('href'):
                        link = title_el['href'] if title_el['href'].startswith('http') else f"https://www.naukri.com{title_el['href']}"

                    results.append({
                        'title': title,
                        'company': company,
                        'location': loc,
                        'description': desc,
                        'stipend': 'Check listing',
                        'apply_url': link or f"https://www.naukri.com/internships-jobs?keyword={quote_plus(query)}",
                        'posted': 'Recent',
                        'skills_extracted': self._extract_skills_from_text(title + ' ' + desc),
                    })
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"Naukri fetch error: {e}")

        return results

    def _fetch_internshala(self, query: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape Internshala for internship listings."""
        results = []
        params = {
            'q': query,
            'city': location or '',
            'source': 'search_srp',
        }
        url = f"https://internshala.com/internships?{urlencode(params)}"

        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            cards = soup.select('div.internship_list_view') or soup.select('div.individual_internship_details') or []

            for card in cards[:max_results]:
                try:
                    title_el = card.select_one('a h3') or card.select_one('h3 a') or card.select_one('a.jobTitle')
                    title = title_el.get_text(strip=True) if title_el else ''
                    if not title:
                        continue

                    company_el = card.select_one('p.company_name') or card.select_one('a.company_name')
                    company = company_el.get_text(strip=True) if company_el else 'Unknown'

                    location_el = card.select_one('p.location_link') or card.select_one('a.location_link')
                    loc = location_el.get_text(strip=True) if location_el else location or 'Work From Home'

                    stipend_el = card.select_one('span.stipend') or card.select_one('p.stipend')
                    stipend = stipend_el.get_text(strip=True) if stipend_el else 'Unpaid'

                    duration_el = card.select_one('span.duration') or card.select_one('p.duration')
                    duration = duration_el.get_text(strip=True) if duration_el else ''

                    link_el = card.select_one('a[href*="/internship/"]')
                    link = ''
                    if link_el and link_el.get('href'):
                        href = link_el['href']
                        link = href if href.startswith('http') else f"https://internshala.com{href}"

                    desc_el = card.select_one('div.internship_description') or card.select_one('p.description')
                    desc = desc_el.get_text(strip=True)[:200] if desc_el else ''

                    date_posted = card.select_one('span.status') or card.select_one('div.status')
                    posted = date_posted.get_text(strip=True) if date_posted else 'Recent'

                    results.append({
                        'title': title,
                        'company': company,
                        'location': loc,
                        'description': desc,
                        'stipend': stipend,
                        'apply_url': link or f"https://internshala.com/internships?{urlencode({'q': query})}",
                        'posted': posted,
                        'duration': duration,
                        'skills_extracted': self._extract_skills_from_text(title + ' ' + desc),
                    })
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"Internshala fetch error: {e}")

        return results

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract mentioned skills from description text."""
        skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql',
            'mongodb', 'html', 'css', 'bootstrap', 'git', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'machine learning', 'deep learning', 'ai',
            'data science', 'data analysis', 'power bi', 'tableau', 'excel',
            'photoshop', 'figma', 'ui/ux', 'product management', 'marketing',
            'seo', 'social media', 'content writing', 'copywriting', 'finance',
            'accounting', 'tally', 'gst', 'taxation', 'business analysis',
            'project management', 'agile', 'scrum', 'sales', 'hr', 'recruitment',
            'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'android', 'ios',
            'flutter', 'react native', 'devops', 'linux', 'networking', 'cybersecurity',
            'blockchain', 'cloud', 'microservices', 'rest api', 'graphql',
            'nlp', 'computer vision', 'tensorflow', 'pytorch', 'pandas', 'numpy',
            'r', 'matlab', 'sas', 'spss', 'autocad', 'solidworks', 'catia',
            'electrical', 'electronics', 'mechanical', 'civil', 'chemical',
            'biotechnology', 'microbiology', 'chemistry', 'physics', 'mathematics',
            'statistics', 'research', 'technical writing', 'communication',
        ]
        text_lower = text.lower()
        found = [s for s in skill_keywords if s in text_lower]
        return list(set(found))[:8]
