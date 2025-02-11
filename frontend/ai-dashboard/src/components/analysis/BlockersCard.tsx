import { Card, Text, List, ListItem } from "@tremor/react";
import { Blockers } from "@/types/analysis";

interface BlockersCardProps {
  blockers: Blockers;
}

export default function BlockersCard({ blockers }: BlockersCardProps) {
  return (
    <Card>
      <Text className="font-medium mb-4 text-black">Project Blockers</Text>
      <div className="space-y-4">
        {blockers.current_blockers.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Current Blockers</Text>
            <List>
              {blockers.current_blockers.map((blocker, index) => (
                <ListItem key={index} className="text-black">{blocker}</ListItem>
              ))}
            </List>
          </div>
        )}

        {blockers.potential_blockers.length > 0 && (
          <div>
            <Text className="text-sm font-medium mb-2 text-gray-700">Potential Blockers</Text>
            <List>
              {blockers.potential_blockers.map((blocker, index) => (
                <ListItem key={index} className="text-black">{blocker}</ListItem>
              ))}
            </List>
          </div>
        )}
      </div>
    </Card>
  );
} 