# EcoTrack - Carbon Footprint Awareness Platform

A web application that helps individuals understand, track, and reduce their carbon footprint through simple actions and personalized insights.

## Vertical

**Carbon Footprint Awareness** — Enabling individuals to measure their environmental impact across transport, diet, home energy, and consumption habits, with tailored recommendations for reduction.

## Approach & Logic

The platform uses a **factor-based carbon estimation model**:

1. **Input Collection** — Users answer simple questions about their lifestyle across four categories:
   - **Transport** — Mode and weekly distance
   - **Diet** — Dietary preference (vegan to high-meat omnivore)
   - **Energy** — Home energy source (renewable, mixed, fossil)
   - **Consumption** — Overall consumption level (minimalist to excessive)

2. **Calculation** — Each input is mapped to a scientifically-grounded carbon factor (tons CO2e/year). The total footprint is the sum of all category contributions.

3. **Categorization** — Results are classified into tiers (excellent, good, average, above average, high) for easy understanding.

4. **Personalized Insights** — The system identifies the highest-contributing categories and surfaces targeted reduction tips, each with estimated CO2 savings.

5. **Tracking** — All calculations are stored in-memory during a session, allowing users to review their history and monitor progress.

## How It Works

1. **Home page** — Overview of the platform with key statistics and calls to action
2. **Calculator** — Form-based input across 4 lifestyle categories
3. **Results** — Detailed breakdown, global comparison, personalized tips, and offset estimation
4. **Tips page** — Comprehensive library of reduction tips organized by category
5. **History** — Table of all past calculations for tracking changes over time
6. **REST API** — JSON endpoint at `/api/calculate` for programmatic access

## Assumptions

- Carbon factors are based on general averages and may not reflect regional variations
- Transport emissions are calculated as annual estimates from weekly distance
- Energy source assumes typical household consumption patterns
- Consumption level is a proxy based on general buying habits
- The platform uses in-memory storage (session-scoped); a database would be needed for persistence across sessions
- Offsetting estimates (trees/hectares) are approximations

## Live Demo

**Deployed on Google Cloud Run:** [https://eco-track-627388336412.us-central1.run.app](https://eco-track-627388336412.us-central1.run.app)

## Tech Stack

- **Backend:** Python Flask
- **Frontend:** HTML, CSS, JavaScript (vanilla, no frameworks)
- **Testing:** pytest
- **Deployment:** gunicorn + Google Cloud Run (containerized via Docker)

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

## Deployment

The app is containerized via Docker and deployed on Google Cloud Run.

```bash
# Build and deploy
gcloud run deploy eco-track --source . --platform managed --region us-central1 --allow-unauthenticated
```

## API

```bash
curl -X POST https://eco-track-627388336412.us-central1.run.app/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "transport_type": "car",
    "transport_distance": "100",
    "diet": "omnivore_medium",
    "energy": "mixed",
    "consumption": "moderate"
  }'
```

## Security

- Content Security Policy headers
- XSS, clickjacking, and MIME-type protections
- Input validation on all user-supplied data
- CSRF protection via Flask's built-in mechanisms

## Accessibility

- Semantic HTML structure (landmarks, headings, ARIA)
- Skip-to-content link
- Keyboard-navigable forms and navigation
- Focus-visible indicators
- Screen reader support (ARIA labels, roles, `aria-live` regions)
- High contrast and reduced motion media query support
- Responsive design for all screen sizes
