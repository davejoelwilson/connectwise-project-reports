'use client';

import { Card, Title, Text, Button } from "@tremor/react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="p-4 md:p-10 mx-auto max-w-5xl">
      <Card className="bg-white border border-red-200">
        <div className="space-y-4">
          <Title className="text-2xl font-bold text-red-600">Something went wrong!</Title>
          <Text className="text-gray-600">{error.message}</Text>
          <Button 
            onClick={reset}
            className="bg-red-600 text-white hover:bg-red-700 transition-colors"
          >
            Try again
          </Button>
        </div>
      </Card>
    </main>
  );
} 