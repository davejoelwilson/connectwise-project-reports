import { Card, Title, Text } from "@tremor/react";

export default function Loading() {
  return (
    <main className="p-4 md:p-10 mx-auto max-w-5xl">
      <div className="mb-10">
        <Title className="text-2xl font-bold text-gray-900 mb-2">Project Analysis Dashboard</Title>
        <Text className="text-gray-600 text-lg">Loading projects...</Text>
      </div>

      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="bg-white border border-gray-200">
            <div className="animate-pulse flex justify-between items-center">
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded w-24"></div>
                <div className="h-4 bg-gray-200 rounded w-72"></div>
              </div>
              <div className="h-4 bg-gray-200 rounded w-24"></div>
            </div>
          </Card>
        ))}
      </div>
    </main>
  );
} 