"""
Setup script para MCP OnBotGo

Este script permite instalar el paquete MCP OnBotGo y sus dependencias.
"""

from setuptools import setup, find_packages
import os

# Leer el README para la descripción larga
def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

# Leer requirements
def read_requirements():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="mcp-onbotgo",
    version="1.0.0",
    author="Equipo OnBotGo",
    author_email="tech@onbotgo.com",
    description="Model Context Protocol Server for OnBotGo Task Management",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/reyer3/mcp-intranet-onbotgo",
    
    packages=find_packages(),
    include_package_data=True,
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business :: Groupware",
    ],
    
    python_requires=">=3.8",
    install_requires=read_requirements(),
    
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "coverage>=7.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocs-mermaid2-plugin>=1.1.0",
        ],
        "production": [
            "uvicorn[standard]>=0.23.0",
            "gunicorn>=21.0.0",
            "prometheus-client>=0.17.0",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "mcp-onbotgo=mcp_onbotgo.server:main",
            "mcp-onbotgo-server=mcp_onbotgo.server:main",
        ],
    },
    
    project_urls={
        "Bug Reports": "https://github.com/reyer3/mcp-intranet-onbotgo/issues",
        "Source": "https://github.com/reyer3/mcp-intranet-onbotgo",
        "Documentation": "https://github.com/reyer3/mcp-intranet-onbotgo/blob/main/docs/",
        "Changelog": "https://github.com/reyer3/mcp-intranet-onbotgo/blob/main/CHANGELOG.md",
    },
    
    keywords=[
        "mcp", "model-context-protocol", "task-management", "ai", "automation",
        "project-management", "productivity", "onbotgo", "api-integration"
    ],
    
    zip_safe=False,
)