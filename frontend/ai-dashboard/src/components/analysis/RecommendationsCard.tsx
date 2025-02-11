import { Card, Text, List, ListItem } from "@tremor/react";
import { Recommendations } from "@/types/analysis";

interface RecommendationsCardProps {
  recommendations: Recommendations;
}

export default function RecommendationsCard({ recommendations }: RecommendationsCardProps) {
  return (
    <Card>
      <Text className="font-medium mb-4 text-black">Recommendations</Text>
      <div className="space-y-4">
        {recommendations.immediate_actions.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Immediate Actions</Text>
            <List>
              {recommendations.immediate_actions.map((action, index) => (
                <ListItem key={index} className="text-black">{action}</ListItem>
              ))}
            </List>
          </div>
        )}

        {recommendations.long_term_improvements.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Long-term Improvements</Text>
            <List>
              {recommendations.long_term_improvements.map((improvement, index) => (
                <ListItem key={index} className="text-black">{improvement}</ListItem>
              ))}
            </List>
          </div>
        )}
      </div>
    </Card>
  );
} 