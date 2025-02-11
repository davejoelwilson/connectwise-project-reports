import { Card, Text } from "@tremor/react";
import { ReactNode } from "react";

interface ErrorBoundaryProps {
  error: Error | null;
  reset: () => void;
  children: ReactNode;
}

export default function ErrorBoundary({ error, reset, children }: ErrorBoundaryProps) {
  if (!error) return <>{children}</>;

  return (
    <Card className="mx-auto max-w-lg mt-8">
      <div className="text-center space-y-4">
        <Text className="text-red-500 font-medium">Something went wrong!</Text>
        <Text className="text-gray-600">{error.message}</Text>
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Try again
        </button>
      </div>
    </Card>
  );
} 