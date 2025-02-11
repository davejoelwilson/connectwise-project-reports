'use client';

import { Card, Title, Text, Select, SelectItem, TextInput, Grid, Col } from "@tremor/react";
import Link from "next/link";
import { useState, useEffect } from "react";

interface Project {
  id: string;
  name: string | { name: string };  // Handle both string and object with name
  company: string | { name: string };
  health_score?: number;
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH';
}

async function getProjects(): Promise<Project[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  const res = await fetch(`${apiUrl}/api/projects`, {
    cache: 'no-store'
  });

  if (!res.ok) {
    throw new Error('Failed to fetch projects');
  }

  const data = await res.json();
  // Transform the data to handle nested objects
  return data.map((project: any) => ({
    id: project.id,
    name: typeof project.name === 'string' ? project.name : project.name?.name || 'Unnamed Project',
    company: typeof project.company === 'string' ? project.company : project.company?.name || 'No Company',
    health_score: undefined,
    risk_level: undefined
  }));
}

async function getProjectAnalysis(projectId: string): Promise<any> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  try {
    const [aiRes, analysisRes] = await Promise.all([
      fetch(`${apiUrl}/api/analysis/${projectId}`),
      fetch(`${apiUrl}/api/projects/${projectId}/analysis`)
    ]);
    
    if (!aiRes.ok || !analysisRes.ok) return null;
    
    const [aiData, analysisData] = await Promise.all([
      aiRes.json(),
      analysisRes.json()
    ]);
    
    return {
      health_score: aiData.health_score,
      risk_level: aiData.risks?.level
    };
  } catch (e) {
    console.error(`Error fetching analysis for project ${projectId}:`, e);
    return null;
  }
}

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [healthFilter, setHealthFilter] = useState("ALL");

  useEffect(() => {
    async function loadProjects() {
      try {
        const projectList = await getProjects();
        
        // Fetch analysis data for each project
        const projectsWithAnalysis = await Promise.all(
          projectList.map(async (project) => {
            const analysis = await getProjectAnalysis(project.id);
            return {
              ...project,
              health_score: analysis?.health_score,
              risk_level: analysis?.risk_level
            };
          })
        );
        
        setProjects(projectsWithAnalysis);
        setLoading(false);
      } catch (error) {
        console.error('Error loading projects:', error);
        setLoading(false);
      }
    }
    
    loadProjects();
  }, []);

  // Filter projects based on search term and filters
  const filteredProjects = projects.filter(project => {
    const projectName = typeof project.name === 'string' ? project.name : project.name.name;
    const companyName = typeof project.company === 'string' ? project.company : project.company.name;
    
    const matchesSearch = 
      projectName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      companyName.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesRisk = riskFilter === "ALL" || project.risk_level === riskFilter;
    
    const matchesHealth = healthFilter === "ALL" || 
      (healthFilter === "HIGH" && (project.health_score || 0) >= 70) ||
      (healthFilter === "MEDIUM" && (project.health_score || 0) >= 40 && (project.health_score || 0) < 70) ||
      (healthFilter === "LOW" && (project.health_score || 0) < 40);
      
    return matchesSearch && matchesRisk && matchesHealth;
  });

  // Sort projects
  const sortedProjects = [...filteredProjects].sort((a, b) => {
    const getProjectName = (p: Project) => typeof p.name === 'string' ? p.name : p.name.name;
    const getCompanyName = (p: Project) => typeof p.company === 'string' ? p.company : p.company.name;
    
    switch (sortBy) {
      case "name":
        return getProjectName(a).localeCompare(getProjectName(b));
      case "company":
        return getCompanyName(a).localeCompare(getCompanyName(b));
      case "health_score":
        return (b.health_score || 0) - (a.health_score || 0);
      case "risk_level":
        const riskOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
        return (riskOrder[a.risk_level || 'LOW'] || 0) - (riskOrder[b.risk_level || 'LOW'] || 0);
      default:
        return 0;
    }
  });

  if (loading) {
    return (
      <main className="p-4 md:p-10 mx-auto max-w-5xl">
        <Title className="text-2xl font-bold text-gray-900 mb-2">Loading...</Title>
      </main>
    );
  }

  return (
    <main className="p-4 md:p-10 mx-auto max-w-5xl">
      <div className="mb-10">
        <Title className="text-2xl font-bold text-gray-900 mb-2">Project Analysis Dashboard</Title>
        <Text className="text-gray-600 text-lg">Select a project to view its analysis</Text>
      </div>

      <div className="mb-6 space-y-4">
        <Grid numItems={1} numItemsSm={2} numItemsLg={4} className="gap-4">
          <Col>
            <Text className="mb-2 text-sm font-medium text-gray-700">Search</Text>
            <TextInput
              placeholder="Search projects or customers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="text-gray-900"
            />
          </Col>
          <Col>
            <Text className="mb-2 text-sm font-medium text-gray-700">Sort By</Text>
            <Select 
              value={sortBy} 
              onValueChange={setSortBy}
              className="text-gray-900 bg-white"
            >
              <SelectItem value="name" className="text-gray-900 bg-white">Project Name (A-Z)</SelectItem>
              <SelectItem value="company" className="text-gray-900 bg-white">Customer Name (A-Z)</SelectItem>
              <SelectItem value="health_score" className="text-gray-900 bg-white">Health Score (High-Low)</SelectItem>
              <SelectItem value="risk_level" className="text-gray-900 bg-white">Risk Level (High-Low)</SelectItem>
            </Select>
          </Col>
          <Col>
            <Text className="mb-2 text-sm font-medium text-gray-700">Risk Level</Text>
            <Select 
              value={riskFilter} 
              onValueChange={setRiskFilter}
              className="text-gray-900 bg-white"
            >
              <SelectItem value="ALL" className="text-gray-900 bg-white">All Risk Levels</SelectItem>
              <SelectItem value="HIGH" className="text-gray-900 bg-white">High Risk</SelectItem>
              <SelectItem value="MEDIUM" className="text-gray-900 bg-white">Medium Risk</SelectItem>
              <SelectItem value="LOW" className="text-gray-900 bg-white">Low Risk</SelectItem>
            </Select>
          </Col>
          <Col>
            <Text className="mb-2 text-sm font-medium text-gray-700">Health Score</Text>
            <Select 
              value={healthFilter} 
              onValueChange={setHealthFilter}
              className="text-gray-900 bg-white"
            >
              <SelectItem value="ALL" className="text-gray-900 bg-white">All Health Scores</SelectItem>
              <SelectItem value="HIGH" className="text-gray-900 bg-white">High Health (70+)</SelectItem>
              <SelectItem value="MEDIUM" className="text-gray-900 bg-white">Medium Health (40-69)</SelectItem>
              <SelectItem value="LOW" className="text-gray-900 bg-white">Low Health (0-39)</SelectItem>
            </Select>
          </Col>
        </Grid>
      </div>

      <div className="space-y-4">
        {sortedProjects.map((project) => (
          <Link key={project.id} href={`/analysis/${project.id}`}>
            <Card className="bg-white border border-gray-200 hover:border-blue-500 hover:scale-[1.02] transition-all cursor-pointer">
              <div className="flex justify-between items-center">
                <div className="space-y-1">
                  <Title className="text-lg font-medium text-gray-900">
                    {typeof project.name === 'string' ? project.name : project.name.name}
                  </Title>
                  <Text className="text-gray-600">
                    {typeof project.company === 'string' ? project.company : project.company.name}
                  </Text>
                </div>
                <div className="flex items-center space-x-4">
                  {project.health_score !== undefined && (
                    <Text className={`font-medium ${
                      project.health_score >= 70 ? 'text-green-600' :
                      project.health_score >= 40 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      Health: {project.health_score}
                    </Text>
                  )}
                  {project.risk_level && (
                    <Text className={`font-medium ${
                      project.risk_level === 'HIGH' ? 'text-red-600' :
                      project.risk_level === 'MEDIUM' ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {project.risk_level} Risk
                    </Text>
                  )}
                  <Text className="text-blue-500">View Analysis →</Text>
                </div>
              </div>
            </Card>
          </Link>
        ))}
        
        {sortedProjects.length === 0 && (
          <Card>
            <Text className="text-center text-gray-600">No projects match your filters</Text>
          </Card>
        )}
      </div>
    </main>
  );
}
