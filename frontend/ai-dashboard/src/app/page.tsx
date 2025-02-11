import { Card, Title, Text } from "@tremor/react";
import Link from "next/link";

interface Project {
  id: string;
  name: string;
  description: string;
}

async function getProjects(): Promise<Project[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  const res = await fetch(`${apiUrl}/api/projects`, {
    cache: 'no-store'  // Only use no-store, remove revalidate
  });

  if (!res.ok) {
    throw new Error('Failed to fetch projects');
  }

  return res.json();
}

export default async function Home() {
  const projects = await getProjects();

  return (
    <main className="p-4 md:p-10 mx-auto max-w-5xl">
      <div className="mb-10">
        <Title className="text-2xl font-bold text-gray-900 mb-2">Project Analysis Dashboard</Title>
        <Text className="text-gray-600 text-lg">Select a project to view its analysis</Text>
      </div>

      <div className="space-y-4">
        {projects.map((project) => (
          <Link key={project.id} href={`/analysis/${project.id}`}>
            <Card className="bg-white border border-gray-200 hover:border-blue-500 hover:scale-[1.02] transition-all cursor-pointer">
              <div className="flex justify-between items-center">
                <div>
                  <Title className="text-lg font-medium text-gray-900">{project.name}</Title>
                  <Text className="text-gray-600">{project.description}</Text>
                </div>
                <Text className="text-blue-500">View Analysis →</Text>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}
