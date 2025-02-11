import { Card, Text, List, ListItem } from "@tremor/react";
import { ProgressAnalysis } from "@/types/analysis";

interface ProgressCardProps {
  progress: ProgressAnalysis;
}

export default function ProgressCard({ progress }: ProgressCardProps) {
  return (
    <Card>
      <Text className="font-medium mb-4 text-black">Progress Analysis</Text>
      <div className="space-y-4">
        <div>
          <Text className="text-sm font-medium mb-1 text-gray-700">Summary</Text>
          <Text className="text-black">{progress.summary}</Text>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Text className="text-sm font-medium mb-1 text-gray-700">Completion Rate</Text>
            <Text className="text-black">{progress.completion_rate}%</Text>
          </div>
          <div>
            <Text className="text-sm font-medium mb-1 text-gray-700">On Track</Text>
            <Text className="text-black">{progress.on_track ? "Yes" : "No"}</Text>
          </div>
        </div>

        {progress.concerns.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Concerns</Text>
            <List>
              {progress.concerns.map((concern, index) => (
                <ListItem key={index} className="text-black">{concern}</ListItem>
              ))}
            </List>
          </div>
        )}
      </div>
    </Card>
  );
} 