import { Card, Text, List, ListItem, Badge } from "@tremor/react";
import { Risk } from "@/types/analysis";

interface RisksCardProps {
  risks: Risk;
}

export default function RisksCard({ risks }: RisksCardProps) {
  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "high":
        return "red";
      case "medium":
        return "yellow";
      case "low":
        return "green";
      default:
        return "gray";
    }
  };

  return (
    <Card>
      <Text className="font-medium mb-4 text-black">Project Risks</Text>
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <Badge color={getRiskColor(risks.level)}>{risks.level}</Badge>
          <Text className="text-black">{risks.factors.join(", ")}</Text>
        </div>
        {risks.mitigation_suggestions && (
          <Text className="text-sm text-gray-700">
            <span className="font-medium">Mitigation:</span> {risks.mitigation_suggestions.join(", ")}
          </Text>
        )}
      </div>
    </Card>
  );
} 