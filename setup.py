from setuptools import setup, find_packages

setup(
    name="connectwise-project-reports",
    version="0.1.0",
    package_dir={"": "backend"},
    packages=find_packages(where="backend"),
    install_requires=[
        "httpx>=0.27.2",
        "python-dotenv>=1.0.1",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.0.0",
        "email-validator>=2.1.0",
        "openai>=1.0.0",
        "agentops>=0.1.0"
    ],
    python_requires=">=3.11",
    author="Dave Wilson",
    author_email="dave@it360.co.nz",
    description="ConnectWise Project Reporting System",
) 