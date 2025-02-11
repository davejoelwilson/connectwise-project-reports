/// <reference types="cypress" />

describe('Project Analysis Page', () => {
  it('should show loading state and then load analysis', () => {
    // Visit analysis page for a known project
    cy.visit('/analysis/4122');
    
    // Check loading state
    cy.get('[data-testid="loading-skeleton"]').should('be.visible');
    
    // Wait for content to load
    cy.get('[data-testid="health-score"]', { timeout: 10000 }).should('be.visible');
    
    // Verify all analysis cards are present
    cy.get('[data-testid="progress-card"]').should('be.visible');
    cy.get('[data-testid="risks-card"]').should('be.visible');
    cy.get('[data-testid="blockers-card"]').should('be.visible');
    cy.get('[data-testid="resource-card"]').should('be.visible');
    cy.get('[data-testid="recommendations-card"]').should('be.visible');
    cy.get('[data-testid="timeline-card"]').should('be.visible');
  });

  it('should show error boundary for invalid project', () => {
    // Visit analysis page with invalid project ID
    cy.visit('/analysis/999999');
    
    // Check error boundary
    cy.get('[data-testid="error-boundary"]').should('be.visible');
    cy.contains('Failed to fetch project analysis').should('be.visible');
    
    // Verify reset button works
    cy.get('[data-testid="reset-button"]').click();
    cy.get('[data-testid="loading-skeleton"]').should('be.visible');
  });
}); 