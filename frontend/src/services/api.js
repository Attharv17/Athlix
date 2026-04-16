import { mockAnalysisData } from '../data/mockAnalysisData';

export const api = {
  /**
   * Returns analysis results from localStorage (set by analyzeMovement).
   * Falls back to squat-specific mockAnalysisData only if no analysis has been run.
   */
  async getAnalysisResults() {
    // Simulate a brief network delay
    return new Promise((resolve) => {
      setTimeout(() => {
        const cached = localStorage.getItem('temp_analysis');
        if (cached) {
          resolve(JSON.parse(cached));
        } else {
          resolve(mockAnalysisData);
        }
      }, 400);
    });
  }
};
