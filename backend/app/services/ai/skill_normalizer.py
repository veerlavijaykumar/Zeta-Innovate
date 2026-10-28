"""Skill normalization and taxonomy service."""
from typing import Optional
from app.services.ai.base import AIService
import structlog

logger = structlog.get_logger()

# Common canonical tech skill mappings
CANONICAL_SKILL_MAP: dict[str, str] = {
    # Frontend
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "vue": "Vue.js",
    "angular.js": "Angular",
    "angularjs": "Angular",
    "angular": "Angular",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "html5": "HTML",
    "html": "HTML",
    "css3": "CSS",
    "css": "CSS",
    
    # Backend
    "py": "Python",
    "python3": "Python",
    "python": "Python",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "golang": "Go",
    "go": "Go",
    "java": "Java",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "c#": "C#",
    "csharp": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "c++": "C++",
    "cpp": "C++",
    "rust": "Rust",
    
    # Data & AI
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elastic": "Elasticsearch",
    "elasticsearch": "Elasticsearch",
    "sql": "SQL",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "spark": "Apache Spark",
    "pyspark": "PySpark",
    "kafka": "Apache Kafka",
    
    # Cloud & DevOps
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "terraform": "Terraform",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "git": "Git",
    "github actions": "GitHub Actions",
    "linux": "Linux",
}

SKILL_CATEGORY_MAP: dict[str, str] = {
    "React": "Frontend",
    "Next.js": "Frontend",
    "Vue.js": "Frontend",
    "Angular": "Frontend",
    "TypeScript": "Programming Language",
    "JavaScript": "Programming Language",
    "HTML": "Frontend",
    "CSS": "Frontend",
    "Tailwind CSS": "Frontend",
    "Python": "Programming Language",
    "FastAPI": "Backend",
    "Django": "Backend",
    "Flask": "Backend",
    "Node.js": "Backend",
    "Express.js": "Backend",
    "Go": "Programming Language",
    "Java": "Programming Language",
    "Spring Boot": "Backend",
    "C#": "Programming Language",
    ".NET": "Backend",
    "C++": "Programming Language",
    "Rust": "Programming Language",
    "PostgreSQL": "Database",
    "MySQL": "Database",
    "MongoDB": "Database",
    "Redis": "Database",
    "Elasticsearch": "Database",
    "SQL": "Database",
    "PyTorch": "AI/ML",
    "TensorFlow": "AI/ML",
    "Scikit-Learn": "AI/ML",
    "Machine Learning": "AI/ML",
    "Deep Learning": "AI/ML",
    "Docker": "DevOps",
    "Kubernetes": "DevOps",
    "AWS": "Cloud",
    "Google Cloud Platform": "Cloud",
    "Microsoft Azure": "Cloud",
    "Terraform": "DevOps",
    "CI/CD": "DevOps",
    "Git": "DevOps",
    "Linux": "DevOps",
}


class SkillNormalizerService:
    """Normalizes skill aliases, taxonomy categories, and provides AI normalization."""

    def __init__(self):
        self.ai = AIService()

    def normalize_skill_name(self, raw_name: str) -> str:
        """Deterministically map common skill names and aliases to their canonical forms."""
        if not raw_name:
            return ""
        clean_key = raw_name.lower().strip()
        return CANONICAL_SKILL_MAP.get(clean_key, raw_name.strip())

    def get_category(self, canonical_name: str) -> str:
        """Return the category for a canonical skill name."""
        return SKILL_CATEGORY_MAP.get(canonical_name, "Technical")

    async def normalize_batch_with_ai(self, raw_skills: list[str]) -> list[dict[str, str]]:
        """Normalize an arbitrary list of raw skill strings using AI if needed."""
        unmapped = []
        result = []

        for skill in raw_skills:
            clean = skill.strip()
            if not clean:
                continue
            canonical = self.normalize_skill_name(clean)
            if canonical.lower() != clean.lower() or clean.lower() in CANONICAL_SKILL_MAP:
                result.append({
                    "raw": clean,
                    "normalized": canonical,
                    "category": self.get_category(canonical),
                })
            else:
                unmapped.append(clean)

        if not unmapped:
            return result

        # Use AI for ambiguous or unseen skills
        try:
            prompt = (
                f"Normalize the following skill names to industry standard canonical names and classify categories. "
                f"Skills: {unmapped}\n"
                f"Return JSON array: [{{\"raw\": \"skill\", \"normalized\": \"Canonical Name\", \"category\": \"Category\"}}]"
            )
            ai_data = await self.ai.generate_json(
                prompt=prompt,
                system_instruction="You are a technical taxonomy expert. Return strictly valid JSON array.",
            )
            if isinstance(ai_data, list):
                result.extend(ai_data)
            elif isinstance(ai_data, dict) and "skills" in ai_data:
                result.extend(ai_data["skills"])
            else:
                for item in unmapped:
                    result.append({"raw": item, "normalized": item, "category": "Technical"})
        except Exception as e:
            logger.warning("AI skill normalization failed, using raw skills", error=str(e))
            for item in unmapped:
                result.append({"raw": item, "normalized": item, "category": "Technical"})

        return result
