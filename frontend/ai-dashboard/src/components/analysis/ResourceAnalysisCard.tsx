import { Card, Text, List, ListItem } from "@tremor/react";
import { ResourceAnalysis } from "@/types/analysis";

interface ResourceAnalysisCardProps {
  resources: ResourceAnalysis;
}

export default function ResourceAnalysisCard({ resources }: ResourceAnalysisCardProps) {
  return (
    <Card>
      <Text className="font-medium mb-4 text-black">Resource Analysis</Text>
      <div className="space-y-4">
        <div>
          <Text className="text-sm font-medium mb-1 text-gray-700">Summary</Text>
          <Text className="text-black">{resources.summary}</Text>
        </div>

        {resources.concerns.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Resource Concerns</Text>
            <List>
              {resources.concerns.map((concern, index) => (
                <ListItem key={index} className="text-black">{concern}</ListItem>
              ))}
            </List>
          </div>
        )}

        {resources.recommendations.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Resource Recommendations</Text>
            <List>
              {resources.recommendations.map((recommendation, index) => (
                <ListItem key={index} className="text-black">{recommendation}</ListItem>
              ))}
            </List>
          </div>
        )}
      </div>
    </Card>
  );
} 