import { Card, Text, Metric } from "@tremor/react";

interface HealthScoreProps {
  score: number;
}

export default function HealthScore({ score }: HealthScoreProps) {
  const getColor = (score: number) => {
    if (score < 40) return "red";
    if (score < 70) return "yellow";
    return "green";
  };

  return (
    <Card className="max-w-xs mx-auto">
      <Text>Project Health Score</Text>
      <Metric color={getColor(score)}>{score}/100</Metric>
    </Card>
  );
} 