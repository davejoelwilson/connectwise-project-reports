import { Grid, Col, Card, Title } from "@tremor/react";

export default function Loading() {
  return (
    <div className="p-4" data-testid="loading-skeleton">
      <div className="mb-8 animate-pulse">
        <Card className="max-w-xs mx-auto h-24" />
      </div>

      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-4">
        {[...Array(6)].map((_, i) => (
          <Col key={i} numColSpan={1}>
            <Card className="h-64 animate-pulse" />
          </Col>
        ))}
      </Grid>
    </div>
  );
} 