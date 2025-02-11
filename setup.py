from setuptools import setup, find_packages

setup(
    name="connectwise-project-reports",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.2",
        "python-dotenv>=1.0.1",
        "streamlit>=1.32.0",
        "plotly>=5.19.0",
        "pandas>=2.2.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "agentops>=0.1.0"
    ],
    python_requires=">=3.11",
    author="Dave Wilson",
    author_email="dave@it360.co.nz",
    description="ConnectWise Project Reporting System",
) 