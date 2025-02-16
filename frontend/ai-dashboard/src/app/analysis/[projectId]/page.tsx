'use client';

import { Grid, Col, Title, Text } from "@tremor/react";
import { Suspense } from "react";
import HealthScore from "@/components/analysis/HealthScore";
import ProgressCard from "@/components/analysis/ProgressCard";
import RisksCard from "@/components/analysis/RisksCard";
import BlockersCard from "@/components/analysis/BlockersCard";
import ResourceAnalysisCard from "@/components/analysis/ResourceAnalysisCard";
import RecommendationsCard from "@/components/analysis/RecommendationsCard";
import TimelinePredictionCard from "@/components/analysis/TimelinePredictionCard";
import { AIAnalysis } from "@/types/analysis";
import Loading from "./loading";
import ErrorBoundary from "@/components/ErrorBoundary";
import React from "react";
import Link from "next/link";
import { ArrowLeftIcon } from "@heroicons/react/24/outline";

async function getProjectAnalysis(projectId: string): Promise<AIAnalysis> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  console.log('Fetching analysis from:', `${apiUrl}/api/analysis/${projectId}`);
  
  // Fetch both AI analysis and regular analysis
  const [aiResponse, analysisResponse] = await Promise.all([
    fetch(`${apiUrl}/api/analysis/${projectId}`),
    fetch(`${apiUrl}/api/projects/${projectId}/analysis`)
  ]);
  
  if (!aiResponse.ok || !analysisResponse.ok) {
    throw new Error(
      aiResponse.status === 404 || analysisResponse.status === 404
        ? "Analysis not found for this project. Please run analysis first." 
        : "Failed to fetch project analysis"
    );
  }

  const [aiData, analysisData] = await Promise.all([
    aiResponse.json(),
    analysisResponse.json()
  ]);

  // Use project name and company from the regular analysis data
  return {
    ...aiData,
    project_name: analysisData.project_name,
    company_name: analysisData.company
  };
}

export default function AnalysisPage({ params }: { params: { projectId: string } }) {
  const [error, setError] = React.useState<Error | null>(null);

  return (
    <div className="p-4 md:p-10 mx-auto max-w-7xl">
      <ErrorBoundary error={error} reset={() => setError(null)}>
        <Suspense fallback={<Loading />}>
          <AnalysisContent 
            projectId={params.projectId} 
            onError={setError}
          />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}

function AnalysisContent({ 
  projectId, 
  onError 
}: { 
  projectId: string;
  onError: (error: Error) => void;
}) {
  const [analysis, setAnalysis] = React.useState<AIAnalysis | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    console.log('AnalysisContent mounted/updated with projectId:', projectId);
    setIsLoading(true);
    getProjectAnalysis(projectId)
      .then(data => {
        console.log('Setting analysis data:', data);
        setAnalysis(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching analysis:', error);
        onError(error);
        setIsLoading(false);
      });
  }, [projectId, onError]);

  if (isLoading) {
    console.log('Rendering loading state');
    return <Loading />;
  }

  if (!analysis) {
    console.log('No analysis data available');
    return (
      <div className="text-center py-12">
        <Title>No Analysis Available</Title>
        <Text className="text-gray-600 mt-2">
          Analysis data could not be loaded for this project.
        </Text>
      </div>
    );
  }

  console.log('Rendering analysis content');
  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <Link 
            href="/"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Projects
          </Link>
          <Title className="text-2xl font-bold text-gray-900 mb-2">
            {analysis.project_name}
          </Title>
          <Text className="text-gray-600 mb-2">
            Customer: {analysis.company_name}
          </Text>
          <Text className="text-gray-600">
            Health Score: {analysis.health_score}/100
          </Text>
        </div>
      </div>

      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-4">
        <Col numColSpan={1}>
          <ProgressCard progress={analysis.progress_analysis} />
        </Col>
        <Col numColSpan={1}>
          <RisksCard risks={analysis.risks} />
        </Col>
        <Col numColSpan={1}>
          <BlockersCard blockers={analysis.blockers} />
        </Col>
        <Col numColSpan={1}>
          <ResourceAnalysisCard resources={analysis.resource_analysis} />
        </Col>
        <Col numColSpan={1}>
          <RecommendationsCard recommendations={analysis.recommendations} />
        </Col>
        <Col numColSpan={1}>
          <TimelinePredictionCard timeline={analysis.timeline_prediction} />
        </Col>
      </Grid>
    </div>
  );
}