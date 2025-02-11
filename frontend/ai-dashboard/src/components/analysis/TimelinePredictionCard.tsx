import { Card, Text, List, ListItem } from "@tremor/react";
import { TimelinePrediction } from "@/types/analysis";

interface TimelinePredictionCardProps {
  timeline: TimelinePrediction;
}

export default function TimelinePredictionCard({ timeline }: TimelinePredictionCardProps) {
  return (
    <Card>
      <Text className="font-medium mb-4 text-black">Timeline Prediction</Text>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Text className="text-sm font-medium mb-1 text-gray-700">Likely Completion</Text>
            <Text className="text-black">{timeline.likely_completion}</Text>
          </div>
          <div>
            <Text className="text-sm font-medium mb-1 text-gray-700">Confidence</Text>
            <Text className="text-black">{timeline.confidence}%</Text>
          </div>
        </div>

        {timeline.factors_affecting_timeline.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Affecting Factors</Text>
            <List>
              {timeline.factors_affecting_timeline.map((factor: string, index: number) => (
                <ListItem key={index} className="text-black">{factor}</ListItem>
              ))}
            </List>
          </div>
        )}
      </div>
    </Card>
  );
} 